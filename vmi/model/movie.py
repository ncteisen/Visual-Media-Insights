class MovieMetadata:
	def __init__(self, imdb_id, title):
		# imdb id for this movie
		self.imdb_id = imdb_id
		# movie title.
		self.title = title


class Movie:
	def __init__(self, imdb_id, title, slug, year, rating, boxoffice):
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
		# integer value of box office money.
		self.boxoffice = boxoffice

	def __str__(self):
		return "Movie[title={title}, year={year}, rating={rating}]".format(
			title=self.title,
			year=self.year,
			rating=self.rating)
