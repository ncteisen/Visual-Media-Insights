import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from pathlib import Path
import logging
from insights.show import ShowInsights

_AUTO_SCALE = True

_BACKGROUND = 'black'
_MIDDLEGROUND = 'gray'
_FOREGROUND = 'white'

_TITLE_SIZE = 20
_SUBTITLE_SIZE = _TITLE_SIZE - 4
_LABEL_SIZE = _SUBTITLE_SIZE - 3

_COLORS = [
    '#e6194b',
    '#3cb44b',
    '#ffe119',
    '#4363d8',
    '#f58231',
    '#911eb4',
    '#46f0f0',
    '#f032e6',
    '#bcf60c',
    '#fabebe',
    '#008080',
    '#e6beff',
    '#9a6324',
    '#fffac8',
    '#800000',
    '#aaffc3',
    '#808000',
    '#ffd8b1',
    '#000075',
]

class Plotter:

    def _subplot_args(self, episode_count):
        return {
            # TODO(ncteisen): support dynamic height
            "figsize": (10 + 5 * max(episode_count / 25, 1), 10), 
            "dpi": 80, 
            "facecolor": _BACKGROUND,
            "sharey": True
        }


    def _format_one_title(self, show):
        return "{title} - {rating}".format(title=show.title, rating=show.rating)


    def _setup(self, show, fig, ax):

        # Set background
        ax.set_facecolor(_BACKGROUND)

        # Set colors to cycle for each season
        ax.set_prop_cycle(color=_COLORS)

        # Title
        ax.set_title(self._format_one_title(show), fontsize=_SUBTITLE_SIZE)

        # Labels
        x_label = "%d episodes" % show.episode_count
        if show.season_count > 1:
            x_label = "{x_label} - {season_count} seasons".format(x_label=x_label, season_count=show.season_count)
        ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


    def _plot(self, show, fig, ax, save = False):

        xlabels = []
        gx, gy = [], []

        for season in show.season_list:
            if not season.episode_list:
                continue

            x = list(map(lambda e: e.index, season.episode_list))
            y = list(map(lambda e: e.score, season.episode_list))

            xlabels.extend(map(lambda e: e.label, season.episode_list))

            gx.extend(x)
            gy.extend(y)

            # Plots the interpolation of season.episode_list for each season.
            sp_x = np.linspace(season.episode_list[0].index, season.episode_list[-1].index, len(season.episode_list) * 10)
            sp_y = interpolate.make_interp_spline(x, y)(sp_x)
            ax.plot(sp_x, sp_y)

            # Plots the per season trend
            z = np.polyfit(x, y, deg=1)
            p = np.poly1d(z)
            ax.scatter(x, y)
            ax.plot(x, p(x), color=_MIDDLEGROUND)

        # Plots the overall show trend.
        gz = np.polyfit(gx, gy, deg=1)
        gp = np.poly1d(gz)
        ax.plot(gx, gp(gx), color=_FOREGROUND)

        # Ticks
        ax.set_xticks(range(1, len(xlabels) + 1))
        ax.set_xticklabels(xlabels, rotation=90)

        if save:
            path = "../img/single/" + show.slug
            plt.savefig(path, bbox_inches="tight")


    def _format_compare_title(self, show1, show2):
        return "{t1} VS {t2}".format(t1=show1.title, t2=show2.title)


    def _format_best_episode(self, show):
        insights = ShowInsights(show)
        best = insights.best_episode
        return "Best:    {label} - {title} ({score}/10)".format(label=best.label, title=best.title, score=best.score)


    def _format_worst_episode(self, show):
        insights = ShowInsights(show)
        worst = insights.worst_episode
        return "Worst:  {label} - {title} ({score}/10)".format(label=worst.label, title=worst.title, score=worst.score)


    def plot_one(self, show):
        logging.info("Plotting %s..." % show.title)
        fig, ax = plt.subplots(**self._subplot_args(show.episode_count))
        ax.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup(show, fig, ax)
        plt.annotate(self._format_best_episode(show), (0,0), (0, -80), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=_LABEL_SIZE)
        plt.annotate(self._format_worst_episode(show), (0,0), (0, -100), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=_LABEL_SIZE)
        self._plot(show, fig, ax, True)
        logging.info("Done!")


    def plot_two(self, show1, show2):
        logging.info("Plotting %s VS %s..." % (show1.title, show2.title))
        fig, (ax1, ax2) = plt.subplots(1, 2, **self._subplot_args(show1.episode_count + show2.episode_count))
        st = fig.suptitle(self._format_compare_title(show1, show2), fontsize=_TITLE_SIZE)
        st.set_y(0.97)
        ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup(show1, fig, ax1)
        self._setup(show2, fig, ax2)
        self._plot(show1, fig, ax1, False)
        self._plot(show2, fig, ax2, False)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        path = "../img/compare/{show1}--VS--{show2}".format(show1=show1.slug, show2=show2.slug)
        plt.savefig(path)
        logging.info("Done!")





