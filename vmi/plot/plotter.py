import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from pathlib import Path

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
    def _setup(self, show):
        fig = plt.figure(
            figsize=(10 + 5 * max(show.episode_count / 25, 1), 7.5),
            dpi=80,
            facecolor=_BACKGROUND
        )

        ax = plt.axes(facecolor=_BACKGROUND)
        ax.set_prop_cycle(color=_COLORS)

        if not _AUTO_SCALE:
            ax.set_ylim(1, 10)
            ax.autoscale(False, axis='y')

        # Title
        plt.title(str(show), fontsize=_TITLE_SIZE)

        # Labels
        x_label = "%d episodes" % show.episode_count

        if show.season_count > 1:
            x_label = "{x_label} - {season_count} seasons".format(x_label=x_label, season_count=show.season_count)

        plt.xlabel(x_label, fontsize=_LABEL_SIZE)
        plt.ylabel("episode score", fontsize=_LABEL_SIZE)

        return fig, ax


    def _setup2(self, show, fig, ax):
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
        fig, ax = self._setup(show)
        self._plot(show, fig, ax, True)


    def plot_two(self, show1, show2):
        fig, (ax1, ax2) = plt.subplots(1, 2, 
            figsize=(10 + 5 * max((show1.episode_count + show2.episode_count) / 25, 1), 7.5), 
            dpi=80, 
            facecolor=_BACKGROUND,
            sharey=True)
        ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup2(show1, fig, ax1)
        self._setup2(show2, fig, ax2)
        # plt.axes(facecolor=_BACKGROUND)
        self._plot(show1, fig, ax1, False)
        self._plot(show2, fig, ax2, False)
        plt.tight_layout()
        path = "../img/{show1}--VS--{show2}".format(show1=show1.slug, show2=show2.slug)
        plt.savefig(path)





