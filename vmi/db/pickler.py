import os
import pickle

from model.show import Show, ShowMetadata

class Pickler:
	def __init__(self, dbpath):
		self.dbpath = dbpath

	def has(self, show):
		return os.path.isfile(self.dbpath + show.imdb_id)

	def get(self, show):
		return pickle.load(open(self.dbpath + show.imdb_id, "rb" ))

	def put(self, show):
		pickle.dump(show, open(self.dbpath + show.imdb_id, "wb" ))


# module testing only
if __name__ == "__main__":
	pickler = Pickler("/tmp/pickles/")
	show = ShowMetadata("Arrested Development", "arrested-development", 8.7, 3)
	assert(not pickler.has(show))
	pickler.put(show)
	assert(pickler.has(show))
	print(pickler.get(show))