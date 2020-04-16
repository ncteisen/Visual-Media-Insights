class Season:
	def __init__(self, number, episode_list):
		# season number.
		self.number = number
		# list of episode_list in the season.
		self.episode_list = episode_list

	@property
	def episode_count(self):
		return len(self.episode_list)