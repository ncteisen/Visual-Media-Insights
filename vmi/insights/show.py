import itertools
import statistics
import sys

from scipy.stats import linregress

from insights.season import SeasonInsights
from model.episode import Episode
from model.season import Season
from model.show import Show
from db.db import DbClient
from util.logger import LoggerConfig

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
	def avg_episode_rating(self):
		return statistics.mean([e.score for e in self.all_episodes])

	@property
	def all_episodes(self):
		return list(itertools.chain.from_iterable([season.episode_list for season in self.show.season_list]))

	@property
	def slope(self):
		return linregress([i for i in range(self.show.episode_count)], [e.score for e in self.all_episodes]).slope
	

if __name__ == "__main__":

	# setup
	LoggerConfig()
	dbclient = DbClient()

	show = dbclient.get_show(sys.argv[1])
	insights = ShowInsights(show)

	print("\n\n\n")
	print("///////////////////////   Show Summary   ////////////////////////")
	print("Overall Show: %s" % show.title)
	print("  slope: {slope_percent:.1f}%".format(slope_percent=insights.slope * 100))
	print("  imdb rating: %s/10"  % show.rating)
	print("  avg episode rating: {avg_episode_rating:.2f}/10".format(
		avg_episode_rating=insights.avg_episode_rating))
	best = insights.best_episode
	print("  best:  {label} - {title} ({score}/10)".format(
		label=best.label,
		title=best.title,
		score=best.score))
	worst = insights.worst_episode
	print("  worst: {label} - {title} ({score}/10)".format(
		label=worst.label,
		title=worst.title,
		score=worst.score))
	print("")

	print("//////////////////////   Seasons Summary   //////////////////////")
	for season in show.season_list:
		insights = SeasonInsights(season)
		print("Season %s" % season.number)
		print("  slope: {slope_percent:.1f}%".format(
			slope_percent=insights.slope * 100))
		print("  avg episode rating: {avg_episode_rating:.2f}/10".format(
			avg_episode_rating=insights.avg_episode_rating))
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