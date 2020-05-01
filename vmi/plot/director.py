import logging
import sys
import unidecode

import matplotlib.pyplot as plt
import numpy as np

from scipy import interpolate

from vmi.db.db import DbClient
from vmi.insights.director import DirectorInsights
from vmi.plot.common import Constants, Saver
from vmi.util.logger import LoggerConfig

_MAX_XLABEL_LEN = 10
_GRAPH_OUTPUT_DIR = "../output/directors/"

def _subplot_args(episode_count):
    return {
        # TODO(ncteisen): support dynamic height
        "figsize": (10 + 5 * max(episode_count / 25, 1), 10), 
        "dpi": 80, 
        "facecolor": Constants.BACKGROUND,
        "sharey": True
    }


def _format_one_title(director):
    return "{title}".format(title=director.name)


def _setup(director, fig, ax):

    # Set background
    ax.set_facecolor(Constants.BACKGROUND)

    # Set colors to cycle for each season
    ax.set_prop_cycle(color=Constants.COLORS)

    # Title
    ax.set_title(_format_one_title(director), fontsize=Constants.SUBTITLE_SIZE)

    # Labels
    x_label = "%d movies" % len(director.movie_list)
    ax.set_xlabel(x_label, fontsize=Constants.LABEL_SIZE)


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
        sp_y = interpolate.make_interp_spline(x, y, k=Constants.SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Plots the per season trend
    z = np.polyfit(x, y, deg=1)
    p = np.poly1d(z)
    ax.scatter(x, y)
    ax.plot(x, p(x), color=Constants.MIDDLEGROUND)

    # Plots the overall show trend.
    gz = np.polyfit(gx, gy, deg=1)
    gp = np.poly1d(gz)
    ax.plot(gx, gp(gx), color=Constants.FOREGROUND)

    # Ticks
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=65)

    insights = DirectorInsights(director)
    _format_footnote_movies(ax, insights)

    if save: Saver.savefig(_GRAPH_OUTPUT_DIR, director.slug)


def _format_movie_title(movie):
    return "{title} - ({rating}/10)".format(
        title=movie.title, rating=movie.rating)


def _format_best_rated_movie(movie):
    return "Best:    {formatted_title}".format(
        formatted_title=_format_movie_title(movie))


def _format_worst_rated_movie(movie):
    return "Worst:  {formatted_title}".format(
        formatted_title=_format_movie_title(movie))

def _format_footnote_movies(ax, insights):
    best = insights.best_rated_movie
    ax.annotate(_format_best_rated_movie(best), (0,0), (0, -80), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=Constants.LABEL_SIZE)
    worst = insights.worst_rated_movie
    ax.annotate(_format_worst_rated_movie(worst), (0,0), (0, -100), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=Constants.LABEL_SIZE)


def plot_one_director(director):
    logging.info("Plotting movies for %s..." % director.name)
    fig, ax = plt.subplots(**_subplot_args(len(director.movie_list)))
    ax.set_ylabel("movie rating", fontsize=Constants.LABEL_SIZE)
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





