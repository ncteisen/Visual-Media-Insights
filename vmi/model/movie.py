class MovieMetadata:
	def __init__(self, imdb_id, title):
		# imdb id for this movie
		self.imdb_id = imdb_id
		# movie title.
		self.title = title


class Movie:
	def __init__(
			self, imdb_id, title, slug, year, rating, budget,
			opening_weekend, boxoffice_usa, boxoffice_worldwide,
			runtime, genre_list):
		# imdb movie id,
		self.imdb_id = imdb_id
		# movie title.
		self.title = title
		# movie slug
		self.slug = slug
		# year the movie was released.
		self.year = year
		# imdb rating for this movie.
		self.rating = rating
		# integer value of the budget.
		self.budget = budget
		self.opening_weekend = opening_weekend
		self.boxoffice_usa = boxoffice_usa
		self.boxoffice_worldwide = boxoffice_worldwide
		self.runtime = runtime
		self.genre_list = genre_list

	def __str__(self):
		return "Movie[title={title}, year={year}, rating={rating}]".format(
			title=self.title,
			year=self.year,
			rating=self.rating)
