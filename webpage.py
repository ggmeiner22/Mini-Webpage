import sys


class Webpage:
    def __init__(self, url, num_links, num_words, links, words, weight):
        self.url = url              # example: https://appstate.edu
        self.num_links = num_links  # number of outgoing links
        self.num_words = num_words  # number of words in the page
        self.links = links          # a list of links
        self.words = words          # a list of words
        self.weight = weight        # importance of the page, using the Pagerank algorithm
