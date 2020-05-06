import itertools
import statistics
import sys

from scipy.stats import linregress

from vmi.model.director import Director
from vmi.model.movie import Movie
from vmi.db.db import DbClient
from vmi.util.logger import LoggerConfig

class DirectorInsights:
	def __init__(self, director):
		self.director = director

	@property
	def worst_rated_movie(self):
		return min(self.director.movie_list, key=lambda m : m.rating)

	@property
	def best_rated_movie(self):
		return max(self.director.movie_list, key=lambda m : m.rating)

	@property
	def avg_movie_rating(self):
		return statistics.mean([m.rating for m in self.director.movie_list])

	@property
	def longest_movie(self):
		return max(self.director.movie_list, key=lambda m : m.runtime)

	@property
	def shortest_movie(self):
		return min(self.director.movie_list, key=lambda m : m.runtime)


if __name__ == "__main__":

	# setup
	LoggerConfig()
	dbclient = DbClient()

	director = dbclient.get_director(sys.argv[1])
	insights = DirectorInsights(director)

	print("\n\n\n")
	print("///////////////////////   Director Summary   ////////////////////////")
	print("Director: %s" % director.name)
	print("  avg movie rating: {avg_movie_rating:.2f}/10".format(
		avg_movie_rating=insights.avg_movie_rating))
	best_movie = insights.best_rated_movie
	print("  best rated:  {title} ({rating}/10)".format(
		title=best_movie.title,
		rating=best_movie.rating))
	worst_movie = insights.worst_rated_movie
	print("  worst rated: {title} ({rating}/10)".format(
		title=worst_movie.title,
		rating=worst_movie.rating))
	print("  avg movie rating: {avg_movie_rating:.2f}/10".format(
		avg_movie_rating=insights.avg_movie_rating))
	print("")

	print("//////////////////////   Movie Summary   //////////////////////")
	for movie in director.movie_list:
		print("Movie %s" % movie.title)
		print("  year: {year}".format(
			year=movie.year))
		print("  rating: {rating:.1f}/10".format(
			rating=movie.rating))
		print("")