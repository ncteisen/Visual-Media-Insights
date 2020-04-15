class Episode:
	def __init__(self, index, season, number, title, score):
		self.index = index
		self.season = season
		self.number = number
		self.title = title
		self.score = score

	@property
	def label(self):
		return "{season:02d}x{number:02d}".format(season=self.season, number=self.number)

	def __str__(self):
		return "{label}: {title}".format(label=self.label, title=self.title)