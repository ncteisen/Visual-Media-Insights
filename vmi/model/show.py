class ShowHandle:
	def __init__(self, title, slug, rating, imdb_id, season_count):
		self.title = title
		self.slug = slug
		self.rating = rating
		self.imdb_id = imdb_id
		self.season_count = season_count



class Show:
	def __init__(self, show_handle):
		self.title = show_handle.title
		self.slug = show_handle.slug
		self.rating = show_handle.rating
		self.imdb_id = show_handle.imdb_id
		self.seasons = {season: [] for season in range(1, show_handle.season_count + 1)}

	@property
	def season_count(self):
		return len(self.seasons)

	@property
	def episode_count(self):
		return sum(map(len, self.seasons.values()))

	def add_episode(self, season, episode):
		self.seasons[season].append(episode)

	def __str__(self):
		return "Show[title={title}, imdb_id={imdb_id}, season_count={season_count}, episode_count={episode_count}]".format(
			title=self.title, 
			imdb_id=self.imdb_id,
			season_count=self.season_count,
			episode_count=self.episode_count)