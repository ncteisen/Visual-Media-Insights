import logging
import sys
import unidecode

import matplotlib.pyplot as plt
import numpy as np

from scipy import interpolate

from db.db import DbClient
from insights.director import DirectorInsights
from util.logger import LoggerConfig

_AUTO_SCALE = True

_BACKGROUND = 'black'
_MIDDLEGROUND = 'gray'
_FOREGROUND = 'white'

_TITLE_SIZE = 20
_SUBTITLE_SIZE = _TITLE_SIZE - 4
_LABEL_SIZE = _SUBTITLE_SIZE - 3

_SPLINE_K = 2

_MAX_XLABEL_LEN = 10

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

_GRAPH_OUTPUT_DIR = "../output/directors/"

def _savefig(fname):
    path = _GRAPH_OUTPUT_DIR + fname
    plt.savefig(path, bbox_inches="tight")

def _subplot_args(episode_count):
    return {
        # TODO(ncteisen): support dynamic height
        "figsize": (10 + 5 * max(episode_count / 25, 1), 10), 
        "dpi": 80, 
        "facecolor": _BACKGROUND,
        "sharey": True
    }


def _format_one_title(director):
    return "{title}".format(title=director.name)


def _setup(director, fig, ax):

    # Set background
    ax.set_facecolor(_BACKGROUND)

    # Set colors to cycle for each season
    ax.set_prop_cycle(color=_COLORS)

    # Title
    ax.set_title(_format_one_title(director), fontsize=_SUBTITLE_SIZE)

    # Labels
    x_label = "%d movies" % len(director.movie_list)
    ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


def _format_xlabel(title):
    if (len(title)) > _MAX_XLABEL_LEN + 3:
        return title[:_MAX_XLABEL_LEN] + "..."
    return title

def _plot(director, fig, ax, save = False):

    xlabels = []
    gx, gy = [], []

    x = range(len(director.movie_list))
    y = list(map(lambda m: m.rating, director.movie_list))

    xlabels.extend(map(lambda m: _format_xlabel(m.title), director.movie_list))

    gx.extend(x)
    gy.extend(y)

    # Plots the interpolation of season.episode_list for each season.
    if (len(director.movie_list) > 3):
        sp_x = np.linspace(0, len(director.movie_list) - 1, len(director.movie_list) * 10)
        sp_y = interpolate.make_interp_spline(x, y, k=_SPLINE_K)(sp_x)
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
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=55)

    if save: _savefig(director.slug)


def plot_one_director(director):
    logging.info("Plotting movies for %s..." % director.name)
    fig, ax = plt.subplots(**_subplot_args(len(director.movie_list)))
    ax.set_ylabel("movie rating", fontsize=_LABEL_SIZE)
    _setup(director, fig, ax)
    _plot(director, fig, ax, True)
    logging.info("Done!")


if __name__ == "__main__":

    # setup
    LoggerConfig()
    dbclient = DbClient()


    argc = len(sys.argv)
    if (argc < 2):
        print("Usage: python -m plot.graph <DIRECTOR ID>")
        raise SystemExit(1)

    show1 = dbclient.get_director(sys.argv[1])
    plot_one_director(show1)





