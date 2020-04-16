import sys
from scipy.stats import linregress
import itertools

from model.episode import Episode
from model.season import Season
from model.show import Show

from db.db import DbClient

class ShowInsights:
	def __init__(self, show):
		self.show = show

	@property
	def worst_episode(self):
		return min(self.all_episodes, key=lambda e : e.score)

	@property
	def best_episode(self):
		return max(self.all_episodes, key=lambda e : e.score)

	@property
	def all_episodes(self):
		return list(itertools.chain.from_iterable([season.episode_list for season in self.show.season_list]))

	@property
	def slope(self):
		return linregress([i for i in range(self.show.episode_count)], [e.score for e in self.all_episodes]).slope
	

# module testing only
if __name__ == "__main__":
	dbclient = DbClient()
	show = dbclient.get_show(sys.argv[1])
	insights = ShowInsights(show)
	print(insights.slope)