import sys
import termios
import tty
import time
from webpage import Webpage

'''
In your search program, include utility.h.
Then call process_keystrokes from main. This has code for real-time input, and it calls the predict method, that takes a string query, and prints the top 5 pages that match that query.
'''

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

def predict(query):
	# this method prints the output for this query. Feel free to change this signature, and pass in the necessary information to print.
	pass

# processes keystrokes one character at a time. Designed for real-time inputs. Call this function from your main program.
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

		if ord(ch[0]) == 8 or ord(ch[0]) == 127: # backspace
			if len(query) > 0:
				query = query[:-1]
		elif ch[0] != '\n':
			query = query + ch


def read_input():
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
			weight=0  # to be computed later using PageRank
		)
		webpages.append(page)

	return webpages


def main():
	pages = read_input()
	# For debugging, you can print the pages or their properties.
	for idx, page in enumerate(pages):
		print(f"Page {idx}: URL: {page.url}")
		print(f"   Number of Words: {page.num_words}")
		#print(f"   Words: {page.words}")
		print(f"   Number of Links: {page.num_links}")
		print(f"   Links (by index): {page.links}")
		print()


main()
