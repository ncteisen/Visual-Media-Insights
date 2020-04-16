class Episode:
	def __init__(self, index, season, number, title, score):
		# overall episode index.
		self.index = index
		# integer season from which this episode was from.
		self.season = season
		# episode number within its season.
		self.number = number
		# episode title.
		self.title = title
		# imdb episode rating
		self.score = score

	@property
	def label(self):
		return "{season:02d}x{number:02d}".format(season=self.season, number=self.number)

	def __str__(self):
		return "{label}: {title}".format(label=self.label, title=self.title)