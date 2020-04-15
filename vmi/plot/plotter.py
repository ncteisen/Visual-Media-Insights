import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from pathlib import Path
import logging

_AUTO_SCALE = True

_BACKGROUND = 'black'
_MIDDLEGROUND = 'gray'
_FOREGROUND = 'white'

_TITLE_SIZE = 16
_LABEL_SIZE = _TITLE_SIZE - 3

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
            "figsize": (10 + 5 * max(episode_count / 25, 1), 7.5), 
            "dpi": 80, 
            "facecolor": _BACKGROUND,
            "sharey": True
        }

    def _setup(self, show, fig, ax):
        ax.set_facecolor(_BACKGROUND)
        ax.set_prop_cycle(color=_COLORS)

        # Title
        ax.set_title(str(show), fontsize=_TITLE_SIZE)

        # Labels
        x_label = "%d episodes" % show.episode_count

        if show.season_count > 1:
            x_label = "{x_label} - {season_count} seasons".format(x_label=x_label, season_count=show.season_count)

        ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


    def _plot(self, show, fig, ax, save = False):

        xlabels = []
        gx, gy = [], []

        for season, episodes in show.seasons.items():
            if not episodes:
                continue

            x = list(map(lambda e: e.index, episodes))
            y = list(map(lambda e: e.score, episodes))

            xlabels.extend(map(lambda e: e.label, episodes))

            gx.extend(x)
            gy.extend(y)

            z = np.polyfit(x, y, deg=1)
            p = np.poly1d(z)

            sp_x = np.linspace(episodes[0].index, episodes[-1].index, len(episodes) * 10)
            sp_y = interpolate.make_interp_spline(x, y)(sp_x)

            ax.plot(sp_x, sp_y)

            ax.scatter(x, y)
            ax.plot(x, p(x), color=_MIDDLEGROUND)

        gz = np.polyfit(gx, gy, deg=1)
        gp = np.poly1d(gz)

        ax.plot(gx, gp(gx), color=_FOREGROUND)

        # Ticks
        ax.set_xticks(range(1, len(xlabels) + 1))
        ax.set_xticklabels(xlabels, rotation=90)

        if save:
            path = "../img" + "/" + show.slug
            plt.savefig(path)


    def plot_one(self, show):
        logging.info("Plotting %s..." % show.title)
        fig, ax = plt.subplots(**self._subplot_args(show.episode_count))
        self._setup(show, fig, ax)
        self._plot(show, fig, ax, True)
        logging.info("Done!")


    def plot_two(self, show1, show2):
        logging.info("Plotting %s VS %s..." % (show1.title, show2.title))
        fig, (ax1, ax2) = plt.subplots(1, 2, **self._subplot_args(show1.episode_count + show2.episode_count))
        ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup(show1, fig, ax1)
        self._setup(show2, fig, ax2)
        self._plot(show1, fig, ax1, False)
        self._plot(show2, fig, ax2, False)
        plt.tight_layout()
        path = "../img/{show1}--VS--{show2}".format(show1=show1.slug, show2=show2.slug)
        plt.savefig(path)
        logging.info("Done!")





