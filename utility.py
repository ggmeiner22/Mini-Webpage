import sys
import termios
import tty
import time

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
	
# processes key strokes one character at a time. Designed for real-time inputs. Call this function from your main program.
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
		

