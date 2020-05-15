import logging
import sys
import unidecode

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from scipy import interpolate

from vmi.db.db import DbClient
from vmi.insights.director import DirectorInsights
from vmi.plot.common import Constants, Saver
from vmi.util.logger import LoggerConfig

_MAX_XLABEL_LEN = 10


def _subplot_args(episode_count):
    return {
        # TODO(ncteisen): support dynamic height
        "figsize": (10 + 5 * max(episode_count / 25, 1), 10),
        "dpi": 80,
        "facecolor": Constants.BACKGROUND,
        "sharey": True
    }


def _format_one_title(director):
    insights = DirectorInsights(director)
    return "{title} - ({rating:.2f}/10)".format(
        title=director.name,
        rating=insights.avg_movie_rating)


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


def _plot_ratings(director, fig, ax, save=False):

    xlabels = []
    gx, gy = [], []

    x = range(len(director.movie_list))
    y = list(map(lambda m: m.rating, director.movie_list))

    xlabels.extend(map(lambda m: _format_xlabel(m.title), director.movie_list))

    gx.extend(x)
    gy.extend(y)

    # Plots the interpolation of season.episode_list for each season.
    if (len(director.movie_list) > Constants.SPLINE_K):
        sp_x = np.linspace(0, len(director.movie_list) - 1,
                           len(director.movie_list) * 10)
        sp_y = interpolate.make_interp_spline(x, y, k=Constants.SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Plots the trend
    z = np.polyfit(x, y, deg=1)
    p = np.poly1d(z)
    ax.scatter(x, y)
    ax.plot(x, p(x), color=Constants.MIDDLEGROUND)

    # Ticks
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=65)

    insights = DirectorInsights(director)
    _format_footnote_movies(ax, insights)

    if save:
        Saver.savefig(Constants.DIRECTOR_OUTPUT_DIR, director.slug + "-rating")


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
    ax.annotate(_format_best_rated_movie(best), (0, 0), (0, -80),
                xycoords='axes fraction',
                textcoords='offset points',
                va='top',
                fontsize=Constants.LABEL_SIZE)
    worst = insights.worst_rated_movie
    ax.annotate(_format_worst_rated_movie(worst), (0, 0), (0, -100),
                xycoords='axes fraction',
                textcoords='offset points',
                va='top',
                fontsize=Constants.LABEL_SIZE)


def _plot_runtime(director, fig, ax, save=False):

    xlabels = []
    gx, gy = [], []

    x = range(len(director.movie_list))
    y = list(map(lambda m: m.runtime, director.movie_list))

    formatter = ticker.FuncFormatter(lambda x, pos: '%d min' % x)
    ax.yaxis.set_major_formatter(formatter)

    xlabels.extend(map(lambda m: _format_xlabel(m.title), director.movie_list))

    gx.extend(x)
    gy.extend(y)

    # Plots the interpolation of movies.
    if (len(director.movie_list) > Constants.SPLINE_K):
        sp_x = np.linspace(0, len(director.movie_list) - 1,
                           len(director.movie_list) * 10)
        sp_y = interpolate.make_interp_spline(x, y, k=Constants.SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Ticks
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=65)

    insights = DirectorInsights(director)
    _format_footnote_movies_runtime(ax, insights)

    if save:
        Saver.savefig(
            Constants.DIRECTOR_OUTPUT_DIR,
            director.slug + "-runtime")


def _plot_budget(director, fig, ax, save=False):

    xlabels = []
    gx, gy = [], []

    x = range(len(director.movie_list))
    y = list(map(lambda m: m.budget, director.movie_list))

    formatter = ticker.FuncFormatter(lambda x, pos: '$%1.1fM' % (x * 1e-6))
    ax.yaxis.set_major_formatter(formatter)

    xlabels.extend(map(lambda m: _format_xlabel(m.title), director.movie_list))

    gx.extend(x)
    gy.extend(y)

    # Plots the interpolation of movies.
    if (len(director.movie_list) > Constants.SPLINE_K):
        sp_x = np.linspace(0, len(director.movie_list) - 1,
                           len(director.movie_list) * 10)
        sp_y = interpolate.make_interp_spline(x, y, k=Constants.SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Ticks
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=65)

    insights = DirectorInsights(director)
    _format_footnote_movies_runtime(ax, insights)

    if save:
        Saver.savefig(
            Constants.DIRECTOR_OUTPUT_DIR,
            director.slug + "-budget")


def _format_movie_title_runtime(movie):
    mins = movie.runtime
    hours = mins // 60
    mins = mins - hours * 60
    return "{title} - {hours} hr {minutes} min".format(
        title=movie.title, hours=hours, minutes=mins)


def _format_longest_rated_movie(movie):
    return "Longest:  {formatted_title}".format(
        formatted_title=_format_movie_title_runtime(movie))


def _format_shortest_rated_movie(movie):
    return "Shortest:  {formatted_title}".format(
        formatted_title=_format_movie_title_runtime(movie))


def _format_footnote_movies_runtime(ax, insights):
    longest = insights.longest_movie
    ax.annotate(_format_longest_rated_movie(longest), (0, 0), (0, -80),
                xycoords='axes fraction',
                textcoords='offset points',
                va='top',
                fontsize=Constants.LABEL_SIZE)
    shortest = insights.shortest_movie
    ax.annotate(_format_shortest_rated_movie(shortest), (0, 0), (0, -100),
                xycoords='axes fraction',
                textcoords='offset points',
                va='top',
                fontsize=Constants.LABEL_SIZE)


def plot_one_director(director):
    logging.info("Plotting movies for %s..." % director.name)
    fig, ax = plt.subplots(**_subplot_args(len(director.movie_list)))
    ax.set_ylabel("movie rating", fontsize=Constants.LABEL_SIZE)
    _setup(director, fig, ax)
    _plot_ratings(director, fig, ax, True)
    logging.info("Done!")


def plot_one_director_runtime(director):
    logging.info("Plotting movies for %s..." % director.name)
    fig, ax = plt.subplots(**_subplot_args(len(director.movie_list)))
    ax.set_ylabel("movie runtime", fontsize=Constants.LABEL_SIZE)
    _setup(director, fig, ax)
    _plot_runtime(director, fig, ax, True)
    logging.info("Done!")


def plot_one_director_budget(director):
    logging.info("Plotting movies for %s..." % director.name)
    fig, ax = plt.subplots(**_subplot_args(len(director.movie_list)))
    ax.set_ylabel("movie budget", fontsize=Constants.LABEL_SIZE)
    _setup(director, fig, ax)
    _plot_budget(director, fig, ax, True)
    logging.info("Done!")


if __name__ == "__main__":

    # setup
    LoggerConfig()
    dbclient = DbClient()

    argc = len(sys.argv)
    if argc < 2:
        print("Usage: python -m plot.graph <DIRECTOR ID>")
        raise SystemExit(1)

    director = dbclient.get_director_by_name(sys.argv[1])

    if argc < 3:
        plot_one_director(director)
    elif sys.argv[2] == "runtime":
        plot_one_director_runtime(director)
    elif sys.argv[2] == "budget":
        plot_one_director_budget(director)
