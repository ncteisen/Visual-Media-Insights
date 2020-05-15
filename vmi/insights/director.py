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
        return min(self.director.movie_list, key=lambda m: m.rating)

    @property
    def best_rated_movie(self):
        return max(self.director.movie_list, key=lambda m: m.rating)

    @property
    def avg_movie_rating(self):
        return statistics.mean([m.rating for m in self.director.movie_list])

    @property
    def longest_movie(self):
        return max(self.director.movie_list, key=lambda m: m.runtime)

    @property
    def shortest_movie(self):
        return min(self.director.movie_list, key=lambda m: m.runtime)


if __name__ == "__main__":

    # setup
    LoggerConfig()
    dbclient = DbClient()

    director = dbclient.get_director_by_name(sys.argv[1])
    insights = DirectorInsights(director)

    print("\n\n\n")
    print("///////////////////////   Director Summary   ////////////////////////")
    print(f"Director: {director.name}")
    print(f"  avg movie rating: {insights.avg_movie_rating:.2f}/10")
    best_movie = insights.best_rated_movie
    print(f"  best rated:  {best_movie.title} ({best_movie.rating}/10)")
    worst_movie = insights.worst_rated_movie
    print(f"  worst rated: {worst_movie.title} ({worst_movie.rating}/10)")
    print(f"  avg movie rating: {insights.avg_movie_rating:.2f}/10")
    print("")

    print("//////////////////////   Movie Summary   //////////////////////")
    for movie in director.movie_list:
        print(f"Movie  {movie.title}")
        print(f"  year: {movie.year}")
        print(f"  rating: {movie.rating:.1f}/10")
        print(f"  budget: {movie.budget}")
        print(f"  opening_weekend: {movie.opening_weekend}")
        print(f"  boxoffice_usa: {movie.boxoffice_usa}")
        print(f"  boxoffice_worldwide: {movie.boxoffice_worldwide}")
        print(f"  runtime: {movie.runtime}")
        print(f"  genre_list: {movie.genre_list}")
        print("")
