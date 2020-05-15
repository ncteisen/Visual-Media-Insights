import statistics
import sys

from scipy.stats import linregress

from vmi.db.db import DbClient
from vmi.model.episode import Episode
from vmi.model.season import Season
from vmi.model.show import Show
from vmi.util.logger import LoggerConfig


class SeasonInsights:
    def __init__(self, season):
        self.season = season

    @property
    def worst_episode(self):
        return min(self.season.episode_list, key=lambda e: e.score)

    @property
    def best_episode(self):
        return max(self.season.episode_list, key=lambda e: e.score)

    @property
    def avg_episode_rating(self):
        return statistics.mean([e.score for e in self.season.episode_list])

    @property
    def slope(self):
        return linregress([i for i in range(self.season.episode_count)], [
                          e.score for e in self.season.episode_list]).slope


# module testing only
if __name__ == "__main__":
    # setup
    LoggerConfig()
    dbclient = DbClient()

    show = dbclient.get_show(sys.argv[1])
    season = show.season_list[int(sys.argv[2]) - 1]
    insights = SeasonInsights(season)

    print("\n\n\n")
    print("/////////////////////   Season Summary   ////////////////////////")
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
