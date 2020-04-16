import os
import pickle
import sys
import logging

from pickler import Pickler

from net.net import Net

class DbClient:
	def __init__(self):
		self.net = Net()
		# TODO(ncteisen): clean up dir pattern
		self.pickler = Pickler("db/pickles/")

	def get_show(self, title):
		logging.info("Getting show %s..." % title)
		show_metadata = self.net.get_show_metadata(title)
		logging.info("Got handle for show %s!" % show_metadata.title)
		if (self.pickler.has(show_metadata)):
			logging.info("Show %s was found in the pickle DB!" % show_metadata.title)
			return self.pickler.get(show_metadata)
		else:
			logging.info("Scraping data for show %s..." % show_metadata.title)
			show = self.net.get_show(show_metadata)
			logging.info("Done scraping data for show %s!" % show_metadata.title)
			self.pickler.put(show)
			return show

# module testing only
if __name__ == "__main__":
	dbclient = DbClient()
	dbclient.get_show(sys.argv[1])