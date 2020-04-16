# Metadata about a particular show.
class ShowMetadata:
	def __init__(self, title, slug, rating, imdb_id, season_count):
		# title of the show.
		self.title = title
		# slugified title, safe for use in filenames.
		self.slug = slug
		# imdb rating of the overall show.
		self.rating = rating
		# imdb id of the show.
		self.imdb_id = imdb_id
		# number of seasons.
		self.season_count = season_count


# All data we care about from a particular show. This will be pickled up into
# our mini, file-based database
class Show:
	def __init__(self, show_metadata, season_list):
		self.title = show_metadata.title
		self.slug = show_metadata.slug
		self.rating = show_metadata.rating
		self.imdb_id = show_metadata.imdb_id
		self.season_list = season_list
		self.season_count = len(season_list)
		self.episode_count = sum(map(lambda season: len(season.episode_list), season_list))

	def __str__(self):
		return "Show[title={title}, imdb_id={imdb_id}, season_count={season_count}, episode_count={episode_count}]".format(
			title=self.title, 
			imdb_id=self.imdb_id,
			season_count=self.season_count,
			episode_count=self.episode_count)