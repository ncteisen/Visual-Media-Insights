import sys

from slugify import slugify

from model.episode import Episode
from model.review import Review
from model.season import Season
from model.show import Show, ShowMetadata
from omdb import OmdbApiClient, OmdbShowData
from imdb import ImdbScraper

class Net:
	def __init__(self):
		self.omdb = OmdbApiClient()
		self.imdb = ImdbScraper()

	# Based on title, attempts to read and parse show metadata.
	def get_show_metadata(self, title):
		omdb_show_data = self.omdb.get_show_data(title)
		return ShowMetadata(
			omdb_show_data.title,
			slugify(unicode(omdb_show_data.title)), 
			omdb_show_data.imdb_rating, 
			omdb_show_data.imdb_id,
			omdb_show_data.season_count)

	# Based on title, attempts to read and parse all episode info about a
	# particular show. Raises an system exist if we encounter any errors.
	def get_show(self, show_metadata):
		imdb_show_data = self.imdb.scrape_show(show_metadata)
		season_list = []
		for i, season in enumerate(imdb_show_data.season_list):
			episode_list = []
			for episode in season.episode_list:
				episode_list.append(Episode(
					episode.index, 
					episode.season, 
					episode.number, 
					episode.title, 
					episode.score,
					episode.imdb_id))
			season_list.append(Season(i + 1, episode_list))
		show = Show(show_metadata, season_list)
		return show

	# Based on imdb_id, attempts to read and parse top 25 reviews.
	def get_reviews(self, imdb_id):
		review_data = self.imdb.scrape_top_reviews(imdb_id)
		review_list = []
		for review in review_data.review_list:
			review_list.append(Review(review.title, review.body))
		return review_list




# module testing only
if __name__ == "__main__":
	if (len(sys.argv)) < 2:
		print("Usage: python -m net.net <TITLE>'")
		raise SystemExit(1)

	net = Net()
	show_metadata = net.get_show_metadata(sys.argv[1])
	show = net.get_show(show_metadata)
	print(show.season_list[0].episode_list[0].imdb_id)
