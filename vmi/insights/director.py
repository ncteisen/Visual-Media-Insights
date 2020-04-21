import itertools
import statistics
import sys

from scipy.stats import linregress

from model.director import Director
from model.movie import Movie
from db.db import DbClient
from util.logger import LoggerConfig

class DirectorInsights:
	def __init__(self, director):
		self.director = director

	@property
	def worst_movie(self):
		return min(self.director.movie_list, key=lambda m : m.rating)

	@property
	def best_movie(self):
		return max(self.director.movie_list, key=lambda m : m.rating)

	@property
	def avg_movie_rating(self):
		return statistics.mean([m.rating for m in self.director.movie_list])
	

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
	best = insights.best_movie
	print("  best:  {title} ({rating}/10)".format(
		title=best.title,
		rating=best.rating))
	worst = insights.worst_movie
	print("  worst: {title} ({rating}/10)".format(
		title=worst.title,
		rating=worst.rating))
	print("")

	print("//////////////////////   Movie Summary   //////////////////////")
	for movie in director.movie_list:
		print("Movie %s" % movie.title)
		print("  year: {year}".format(
			year=movie.year))
		print("  rating: {rating:.1f}/10".format(
			rating=movie.rating))
		print("")