import sys
from scipy.stats import linregress

from model.episode import Episode
from model.season import Season
from model.show import Show

from db.db import DbClient

class SeasonInsights:
	def __init__(self, season):
		self.season = season

	@property
	def worst_episode(self):
		return min(self.season.episode_list, key=lambda e : e.score)

	@property
	def best_episode(self):
		return max(self.season.episode_list, key=lambda e : e.score)

	@property
	def slope(self):
		return linregress([i for i in range(self.season.episode_count)], [e.score for e in self.season.episode_list]).slope


# module testing only
if __name__ == "__main__":
	dbclient = DbClient()
	show = dbclient.get_show(sys.argv[1])
	for season in show.season_list:
		insights = SeasonInsights(season)
		print("Season %s" % season.number)
		print("  slope: %f" % insights.slope)
		best = insights.best_episode
		print("  best:  ({number}/{episode_count}) {title} ({score}/10)".format(
			number=best.number,
			episode_count=season.episode_count,
			title=best.title,
			score=best.score))
		worst = insights.worst_episode
		print("  worst: ({number}/{episode_count}) {title} ({score}/10)".format(
			number=worst.number,
			episode_count=season.episode_count,
			title=worst.title,
			score=worst.score))
		print("")