import sys

from slugify import slugify

from model.show import Show, ShowHandle
from omdb import OmdbApiClient, OmdbShowData
from imdb import ImdbScraper

class Net:
	def __init__(self):
		self.omdb = OmdbApiClient()
		self.imdb = ImdbScraper()

	def get_show_handle(self, title):
		omdb_show_info = self.omdb.get_show_data(title)
		return ShowHandle(
			omdb_show_info.title,
			slugify(unicode(omdb_show_info.title)), 
			omdb_show_info.imdb_rating, 
			omdb_show_info.imdb_id,
			omdb_show_info.season_count)

	# Based on title, attempts to read and parse all episode info about a
	# particular show. Raises an system exist if we encounter any errors.
	def parse_show(self, show_handle):
		# TODO(ncteisen): unlink model from imdb scraper
		show = Show(show_handle)
		self.imdb._scrape_episodes(show)
		return show



# module testing only
if __name__ == "__main__":
	if (len(sys.argv)) < 2:
		print("Usage: python -m net.net <TITLE>'")
		raise SystemExit(1)

	net = Net()
	# show = net.parse_show(sys.argv[1])
	print net.get_sluggified_title(sys.argv[1])
