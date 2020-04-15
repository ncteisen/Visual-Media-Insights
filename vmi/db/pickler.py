import os
import pickle

from model.show import Show, ShowHandle

class Pickler:
	def __init__(self, dbpath):
		self.dbpath = dbpath

	def has(self, show):
		return os.path.isfile(self.dbpath + show.slug)

	def get(self, show):
		return pickle.load(open(self.dbpath + show.slug, "rb" ))

	def put(self, show):
		pickle.dump(show, open(self.dbpath + show.slug, "wb" ))


# module testing only
if __name__ == "__main__":
	pickler = Pickler("/tmp/pickles/")
	show = ShowHandle("Arrested Development", "arrested-development", 8.7, 3)
	assert(not pickler.has(show))
	pickler.put(show)
	assert(pickler.has(show))
	print pickler.get(show)