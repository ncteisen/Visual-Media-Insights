import sys

from slugify import slugify

from vmi.model.director import DirectorMetadata
from vmi.model.episode import Episode
from vmi.model.movie import Movie, MovieMetadata
from vmi.model.review import Review
from vmi.model.season import Season
from vmi.model.show import Show, ShowMetadata
from vmi.net.omdb import OmdbApiClient, OmdbShowData
from vmi.net.imdb import ImdbScraper

class Net:
	def __init__(self):
		self.omdb = OmdbApiClient()
		self.imdb = ImdbScraper()

	# Based on title, attempts to read and parse show metadata.
	def get_show_metadata(self, title):
		omdb_show_metadata = self.omdb.get_show_metadata(title)
		return ShowMetadata(
			title=omdb_show_metadata.title,
			slug=slugify(omdb_show_metadata.title), 
			rating=omdb_show_metadata.imdb_rating, 
			imdb_id=omdb_show_metadata.imdb_id,
			season_count=omdb_show_metadata.season_count)

	# Based on title, attempts to read and parse all episode info about a
	# particular show. Raises an system exist if we encounter any errors.
	def get_show(self, show_metadata):
		imdb_show_data = self.imdb.scrape_show(show_metadata)
		season_list = []
		for i, season in enumerate(imdb_show_data.season_list):
			episode_list = []
			for episode in season.episode_list:
				episode_list.append(Episode(
					index=episode.index, 
					season=episode.season, 
					number=episode.number, 
					title=episode.title, 
					score=episode.score,
					imdb_id=episode.imdb_id))
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

	def get_director_metadata(self, imdb_id):
		director_data = self.imdb.scrape_director(imdb_id)
		movie_metadata_list = []
		for movie_metadata in director_data.movie_metadata_list:
			movie_metadata_list.append(MovieMetadata(
				imdb_id=movie_metadata.imdb_id,
				title=movie_metadata.title))
		return DirectorMetadata(
			imdb_id=imdb_id,
			name=director_data.name,
			slug=slugify(director_data.name),
			movie_metadata_list=movie_metadata_list)

	def get_movie(self, movie_metadata):
		omdb_movie_data = self.omdb.get_movie_data(movie_metadata)
		imdb_movie_data = self.imdb.scrape_movie(movie_metadata.imdb_id)
		return Movie(
			imdb_id=omdb_movie_data.imdb_id,
			title=omdb_movie_data.title,
			slug=slugify(omdb_movie_data.title),
			year=omdb_movie_data.year,
			rating=omdb_movie_data.imdb_rating,
			budget=imdb_movie_data.budget,
			opening_weekend=imdb_movie_data.opening_weekend,
			boxoffice_usa=imdb_movie_data.us_boxoffice,
			boxoffice_worldwide=imdb_movie_data.worldwide_boxoffice,
			runtime=imdb_movie_data.runtime,
			genre_list=imdb_movie_data.genre_list)


# module testing only
if __name__ == "__main__":
	if (len(sys.argv)) < 2:
		print("Usage: python -m net.net <TITLE>'")
		raise SystemExit(1)

	net = Net()
	director = net.get_director_metadata(sys.argv[1])
	for movie_metadata in director.movie_metadata_list:
		movie = net.get_movie(movie_metadata)
		print(movie)
