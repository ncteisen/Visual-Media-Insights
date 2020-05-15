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
    print(f"Season {season.number}")
    print(f"  slope: {insights.slope * 100:.1f}%")
    print(f"  avg episode rating: {insights.avg_episode_rating:.2f}/10")
    b = insights.best_episode
    print(
        f"  best:  ({b.number}/{season.episode_count}) {b.title} ({b.score}/10)")
    w = insights.worst_episode
    print(
        f"  worst: ({w.number}/{season.episode_count}) {w.title} ({w.score}/10)")
