import os
import pickle
import sys
import logging

from db.pickler import Pickler
from model.director import Director
from net.net import Net
from util.logger import LoggerConfig

_PICKLE_DATA_DIR = "../data/pickles/"

class FakeDirectorMetadata:
	def __init__(self):
		imdb_id = None

class DbClient:
	def __init__(self):
		self.net = Net()
		self.pickler = Pickler(_PICKLE_DATA_DIR)

	def get_show(self, title):
		logging.info("Getting show %s..." % title)
		show_metadata = self.net.get_show_metadata(title)
		logging.info("Got handle for show %s!" % show_metadata.title)
		if (self.pickler.has(show_metadata)):
			logging.info("Show %s was found in the pickle DB!" % show_metadata.title)
			show = self.pickler.get(show_metadata)
		logging.info("Scraping data for show %s..." % show_metadata.title)
		show = self.net.get_show(show_metadata)
		logging.info("Done scraping data for show %s!" % show_metadata.title)
		self.pickler.put(show)
		return show

	def _get_director_metadata(self, imdb_id):
		logging.info("Getting director...")
		# HACK
		director_metadata = FakeDirectorMetadata()
		director_metadata.imdb_id = imdb_id
		if (self.pickler.has(director_metadata)):
			director_metadata = self.pickler.get(director_metadata)
			logging.info("Director %s was found in the pickle DB!" % director_metadata.name)
			return director_metadata
		logging.info("Scraping data for director...")
		director_metadata = self.net.get_director_metadata(director_metadata.imdb_id)
		logging.info("Done scraping data for director %s!" % director_metadata.name)
		self.pickler.put(director_metadata)
		return director_metadata

	def _get_movie(self, movie_metadata):
		logging.info("Getting movie %s..." % movie_metadata.title)
		if (self.pickler.has(movie_metadata)):
			movie_metadata = self.pickler.get(movie_metadata)
			logging.info("Movie %s was found in the pickle DB!" % movie_metadata.title)
			return movie_metadata
		logging.info("Scraping data for movie...")
		movie = self.net.get_movie(movie_metadata)
		logging.info("Done scraping data for movie %s!" % movie_metadata.title)
		self.pickler.put(movie)
		return movie


	def get_director(self, imdb_id):
		director_metadata = self._get_director_metadata(imdb_id)
		movie_list = []
		for movie_metadata in director_metadata.movie_metadata_list:
			movie_list.append(self._get_movie(movie_metadata))
		movie_list.reverse()
		return Director(director_metadata, movie_list)



# module testing only
if __name__ == "__main__":
	# setup
	LoggerConfig()
	dbclient = DbClient()
	dbclient.get_director(sys.argv[1])