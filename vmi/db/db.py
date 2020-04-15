import os
import pickle
import sys

from pickler import Pickler

from net.net import Net

class DbClient:
	def __init__(self):
		self.net = Net()
		# TODO(ncteisen): clean up dir pattern
		self.pickler = Pickler("db/pickles/")

	def get_show(self, title):
		show_handle = self.net.get_show_handle(title)
		if (self.pickler.has(show_handle)):
			return self.pickler.get(show_handle)
		else:
			show = self.net.parse_show(show_handle)
			self.pickler.put(show)
			return show

# module testing only
if __name__ == "__main__":
	dbclient = DbClient()
	dbclient.get_show(sys.argv[1])