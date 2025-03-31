import sys
import termios
import tty
import time
from webpage import Webpage

# Global variables for pages and the word index
pages = []          # list of Webpage objects built from read_input()
words_array = []    # list of word records and each is a dictionary
word_to_index = {}  # maps a normalized word to its index in words_array

# Color variables
clear_screen = "\x1b[2J\x1b[H"
color_black = "\u001b[30m"
color_red = "\u001b[31m"
color_green = "\u001b[32m"
color_yellow = "\u001b[33m"
color_blue = "\u001b[34m"
color_magenta = "\u001b[35m"
color_cyan = "\u001b[36m"
color_white = "\u001b[37m"
color_reset = "\u001b[0m"

color_bkgnd_yellow = "\u001b[43;1m"
color_bkgnd_black = "\u001b[40;1m"


def build_word_index():
	"""
	Builds a word index from the global 'pages' list.
	:return: A tuple (words_array, word_to_index) where
		words_array is a list of dictionaries, each with 3 keys.
		"text" is the normalized word,
		"pages" is a list of page IDs where the word occurs,
		"num_pages" is the count of pages containing the word.
		word_to_index is a dictionary mapping each normalized word to its index in words_array.
	"""
	# Map from word (normalized) to list of page IDs.
	word_page_map = {}
	for i, page in enumerate(pages):
		seen_in_page = set()  # Avoid adding the same page multiple times for one word.
		for word in page.words:
			normalized_word = word.lower()  # Normalizes the word for case-insensitive matching

			if normalized_word not in seen_in_page:
				seen_in_page.add(normalized_word)
				# If the normalized word is not already a key in word_page_map, it is added with an empty list.
				# Then the current page ID, i, is appended to that list.
				if normalized_word not in word_page_map:
					word_page_map[normalized_word] = []
				word_page_map[normalized_word].append(i)

	# Builds the words_array and its hash map.
	temp_words_array = []
	temp_word_to_index = {}
	for word, pages_list in word_page_map.items():
		record = {
			"text": word,
			"pages": pages_list,
			"num_pages": len(pages_list)
		}
		index = len(temp_words_array)
		temp_words_array.append(record)
		temp_word_to_index[word] = index

	return temp_words_array, temp_word_to_index


def get_snippet(page, query, context=5):
	"""
	Creates a colored snippet from the page showing the query word in context.
	:param page: A Webpage object with a 'words' list.
	:param query: The search query word.
	:param context: Number of words to include before and after the query (default 5).
	:return: A string snippet where the query is highlighted in red and context words in green.
	"""

	# converts the list of words from the page to lower-case for a case-insensitive search
	lower_words = [w.lower() for w in page.words]
	try:
		# Find first occurrence (case-insensitive) of the query word
		index = lower_words.index(query.lower())
	except ValueError:
		index = 0  # if not found, use the beginning.

	# calculates the start and end indices for the snippet based on a context window
	start = max(0, index - context)
	end = min(len(page.words), index + context + 1)
	snippet_words = page.words[start:end]

	# Highlights the query word in the snippet.
	snippet_highlighted = []
	for w in snippet_words:
		# If w is the searched word, make it red, green otherwise
		if w.lower() == query.lower():
			snippet_highlighted.append(color_red + w + color_reset)
		else:
			snippet_highlighted.append(color_green + w + color_reset)
	# Returns the joined strings
	return " ".join(snippet_highlighted)


def predict(query):
	"""
	Searches for the query word and prints matching pages.
	Displays total matches and up to 5 pages, sorted by descending weight.
	:param query: The search word.
	:return: None, but results are printed.
	"""

	# If the query string is empty, it prints a prompt
	if query == "":
		print("Enter search word:")
		return

	# Search for the word in the hashmap
	normalized_query = query.lower()
	if normalized_query not in word_to_index:
		print(f"No pages contain the word '{query}'.")
		return

	# Retrieve the word record from the index
	record = words_array[word_to_index[normalized_query]]
	total_matches = record["num_pages"]
	print(f"{color_yellow}{total_matches}{color_green} pages match{color_reset}\n")

	# Sort the page IDs by decreasing weights
	sorted_page_ids = sorted(record["pages"], key=lambda pid: pages[pid].weight, reverse=True)

	# Display at most 5 pages
	count = 1
	for page_id in sorted_page_ids:
		if count > 5:
			break
		page = pages[page_id]  # Get the page
		formatted_weight = format_weight(page.weight)
		print(f"{count}. {color_red}[{formatted_weight}]{color_reset} {page.url}")
		snippet = get_snippet(page, query)  # Get the snippet
		print(snippet)
		count += 1


def format_weight(w):
	"""
	Formats a weight value by truncating it to 3 decimal places and sometimes rounding up.
	Rounds up (adds 0.001) if the fourth decimal digit is 9 or higher, then returns the value
	as a string with no trailing zeros or dot.
	:param w: The weight value (float).
	:return: A string representation of w with up to 3 decimal places.
	"""
	# Truncate to 3 decimals
	truncated = int(w * 1000) / 1000
	# Determine the fourth decimal digit
	fourth_digit = int(w * 10000) % 10
	if fourth_digit == 9:
		truncated += 0.001  # round up if the fourth digit is 9

	# Convert to string and remove trailing zeros and dot if needed
	s = f"{truncated:.3f}"  # Ensure up to 3 decimals
	# Remove trailing zeros and an unnecessary dot
	s = s.rstrip('0').rstrip('.')
	return s


# processes keystrokes one character at a time. Designed for real-time inputs
# Call this function from your main program
def process_keystrokes():
	query = ''
	ch = ' '

	fd = sys.stdin.fileno()

	while ch[0] != '\n' and ch[0] != '\r':

		sys.stdout.write(clear_screen)
		sys.stdout.write(color_green + "Search keyword: ")
		sys.stdout.write(color_white + query + color_green + "-\n\n")

		predict(query)
		sys.stdout.write(color_reset)
		sys.stdout.flush()

		old = termios.tcgetattr(fd)
		tty.setraw(fd)
		ch = sys.stdin.read(1)
		time.sleep(.1)
		termios.tcsetattr(fd, termios.TCSADRAIN, old)
		sys.stdin.flush()

		if ord(ch[0]) == 8 or ord(ch[0]) == 127:  # backspace
			if len(query) > 0:
				query = query[:-1]
		elif ch[0] != '\n':
			query = query + ch


def pagerank():
	"""
	Computes PageRank scores for a list of pages and updates each page's weight.
	:return: None. The pages' weights are updated in place.
	"""
	N = len(pages)  # Length of pages
	iterations = 50  # The number of iterations

	# Perform the iterative weight redistribution
	for _ in range(iterations):
		# Create a new list 'new_weights' to hold the updated weight for each page.
		# Each page starts with a base weight of 0.1 due to the teleportation factor
		new_weights = [0.1 for _ in range(N)]

		# Loop over each page along with its index i
		for i, page in enumerate(pages):
			# Check if the page has any outgoing links.
			if page.num_links > 0:
				# Calculate the amount of weight to distribute from page i
				share = 0.9 * page.weight / page.num_links
				# Loop over each linked page indexed j in page i's list of links.
				for j in page.links:
					# Add the calculated share of weight to the new weight of the linked page.
					new_weights[j] += share
			else:
				# If no outgoing links, keep 90% of weight on itself.
				new_weights[i] += 0.9 * page.weight

		# Update the weight for each page.
		for i in range(N):
			pages[i].weight = new_weights[i]


def read_input():
	"""
	Reads the 'asu-domain.txt' file, processes its content, and returns a list of Webpage objects.
	The file is expected to have blocks separated by empty lines, where each block contains:
		- A URL line starting with "URL:"
		- A content line starting with "CONTENT:"
		- A links line starting with "LINKS:"
	:return: A list of Webpage objects.
	"""
	# Read the file into an array of lines
	with open("asu-domain.txt", 'r') as f:
		lines = [line.rstrip() for line in f]

	# Split into blocks separated by empty lines where each block corresponds to one webpage
	blocks = []
	current_block = []  # temporary list that collects lines until an empty line is encountered
	for line in lines:
		if line == "":  # Current line is empty (one block has ended)
			if current_block:
				# reset to an empty list
				blocks.append(current_block)
				current_block = []
		else:
			current_block.append(line)  # if not empty, the current line is appended to blocks
	if current_block:
		blocks.append(current_block)  # Add an extra data that wasn't added if file did not end with empty line

	# Assign each webpage a unique identifier, its index, and create a hash map of internal URLs to these indices.
	url_to_index = {}
	for block in blocks:
		for line in block:
			# Find the URL and clean it
			if line.startswith("URL:"):
				url = line[len("URL:"):].strip()
				# Assign each URL and index if the URL isn’t already in url_to_index
				if url not in url_to_index:
					url_to_index[url] = len(url_to_index)
				break  # move on to the next block once the URL is found

	# Loop through again, creating an array of Webpage objects
	webpages = []
	for block in blocks:
		url = None
		content = ""
		links_line = ""
		for line in block:
			# Extract and clean URL
			if line.startswith("URL:"):
				url = line[len("URL:"):].strip()
			# Extract and clean the webpage's content
			elif line.startswith("CONTENT:"):
				content = line[len("CONTENT:"):].strip()
			# Extract and clean the webpage's links
			elif line.startswith("LINKS:"):
				links_line = line[len("LINKS:"):].strip()
		if url is None:
			continue  # skip if no URL is present

		# Process content into words and number of words
		words = content.split()
		num_words = len(words)

		# Process links by splitting into candidate links and filter out external ones.
		# Also convert each valid link into the index from our url_to_index hash map.

		possible_links = links_line.split()  # List of possible links
		internal_links = []  # List of valid, internal links
		for link in possible_links:
			# If the link has been passed in as a valid webpage in the system, add it to internal_links
			if link in url_to_index:
				internal_links.append(url_to_index[link])
		num_links = len(internal_links)

		# Create the Webpage object
		page = Webpage(
			url=url,
			num_links=num_links,
			num_words=num_words,
			links=internal_links,
			words=words,
			weight=1  # to be computed later using PageRank
		)
		webpages.append(page)

	return webpages


def main():
	global pages, words_array, word_to_index

	# Takes the input in from the input file and stores it into webpage objects
	pages = read_input()

	# Run the PageRank algorithm to compute weights.
	pagerank()

	# Build the index from the pages array.
	words_array, word_to_index = build_word_index()
	# Now run the interactive search interface.
	process_keystrokes()


main()
