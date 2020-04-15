from slugify import slugify

class Show:
	def __init__(self, title, rating, season_count):
		self.title = title
		self.slug = slugify(unicode(title))
		self.rating = rating
		self.seasons = {season: [] for season in range(1, season_count + 1)}

	@property
	def season_count(self):
		return len(self.seasons)

	@property
	def episode_count(self):
		return sum(map(len, self.seasons.values()))

	def add_episode(self, season, episode):
		self.seasons[season].append(episode)

	def __str__(self):
		return "{title} - {rating}".format(title=self.title, rating=self.rating)