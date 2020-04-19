import logging
import sys
import unidecode

import matplotlib.pyplot as plt
import numpy as np

from scipy import interpolate

from db.db import DbClient
from insights.show import ShowInsights
from insights.season import SeasonInsights
from util.logger import LoggerConfig

_AUTO_SCALE = True

_BACKGROUND = 'black'
_MIDDLEGROUND = 'gray'
_FOREGROUND = 'white'

_TITLE_SIZE = 20
_SUBTITLE_SIZE = _TITLE_SIZE - 4
_LABEL_SIZE = _SUBTITLE_SIZE - 3

_SPLINE_K = 2

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

_GRAPH_OUTPUT_DIR = "../output/graphs/"

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


def _format_one_title(show):
    return "{title} - ({rating}/10)".format(title=show.title, rating=show.rating)


def _format_season_title(show, season, insights):
    return "{title}, season {number} ({rating:.2f}/10)".format(
        title=show.title, 
        number=season.number, 
        rating=insights.avg_episode_rating)


def _setup_season(show, season, fig, ax):

    # Set background
    ax.set_facecolor(_BACKGROUND)

    # Set colors to cycle for each season
    # TODO, not needed.
    ax.set_prop_cycle(color=_COLORS)

    # Title
    insights = SeasonInsights(season)
    ax.set_title(_format_season_title(show, season, insights), fontsize=_SUBTITLE_SIZE)

    # Labels
    x_label = "%d episodes" % season.episode_count
    ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


def _setup(show, fig, ax):

    # Set background
    ax.set_facecolor(_BACKGROUND)

    # Set colors to cycle for each season
    ax.set_prop_cycle(color=_COLORS)

    # Title
    ax.set_title(_format_one_title(show), fontsize=_SUBTITLE_SIZE)

    # Labels
    x_label = "%d episodes" % show.episode_count
    if show.season_count > 1:
        x_label = "{x_label} - {season_count} seasons".format(x_label=x_label, season_count=show.season_count)
    ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


def _plot(show, fig, ax, save = False):

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
        if (season.episode_count > 3):
            sp_x = np.linspace(season.episode_list[0].index, season.episode_list[-1].index, len(season.episode_list) * 10)
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

    insights = ShowInsights(show)
    _format_footnote_episodes(ax, insights)

    # Ticks
    ax.set_xticks(range(1, len(xlabels) + 1))
    ax.set_xticklabels(xlabels, rotation=90)

    if save: _savefig(show.slug)

def _plot_season(show, season, fig, ax, save = False):

    xlabels = []
    gx, gy = [], []

    x = list(map(lambda e: e.number, season.episode_list))
    y = list(map(lambda e: e.score, season.episode_list))

    xlabels.extend(map(lambda e: e.label, season.episode_list))

    gx.extend(x)
    gy.extend(y)

    # Plots the interpolation of season.episode_list for each season.
    if (season.episode_count > 3):
        sp_x = np.linspace(season.episode_list[0].number, season.episode_list[-1].number, len(season.episode_list) * 10)
        sp_y = interpolate.make_interp_spline(x, y, k=_SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Plots the per season trend
    z = np.polyfit(x, y, deg=1)
    p = np.poly1d(z)
    ax.scatter(x, y)
    ax.plot(x, p(x), color=_MIDDLEGROUND)

    insights = SeasonInsights(season)
    _format_footnote_episodes(ax, insights)

    # Ticks
    ax.set_xticks(range(1, len(xlabels) + 1))
    ax.set_xticklabels(xlabels, rotation=90)

    if save: _savefig(show.slug + "-season-" + str(season.number))


def _format_compare_title(show1, show2):
    return "{t1} VS {t2}".format(t1=show1.title, t2=show2.title)


def _format_best_episode(episode):
    return "Best:    {label} - {title} ({score}/10)".format(
        label=episode.label,
        title=unidecode.unidecode(episode.title),
        score=episode.score)


def _format_worst_episode(episode):
    return "Worst:  {label} - {title} ({score}/10)".format(
        label=episode.label,
        title=unidecode.unidecode(episode.title),
        score=episode.score)

def _format_footnote_episodes(ax, insights):
    best = insights.best_episode
    ax.annotate(_format_best_episode(best), (0,0), (0, -80), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=_LABEL_SIZE)
    worst = insights.worst_episode
    ax.annotate(_format_worst_episode(worst), (0,0), (0, -100), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=_LABEL_SIZE)


def plot_one_show(show):
    logging.info("Plotting %s..." % show.title)
    fig, ax = plt.subplots(**_subplot_args(show.episode_count))
    ax.set_ylabel("episode score", fontsize=_LABEL_SIZE)
    _setup(show, fig, ax)
    _plot(show, fig, ax, True)
    logging.info("Done!")

def plot_one_season(show, season):
    logging.info("Plotting season %d for %s..." % (season.number, show.title))
    fig, ax = plt.subplots(**_subplot_args(season.episode_count))
    ax.set_ylabel("episode score", fontsize=_LABEL_SIZE)
    _setup_season(show, season, fig, ax)
    _plot_season(show, season, fig, ax, True)
    logging.info("Done!")


def plot_two_shows(show1, show2):
    logging.info("Plotting %s VS %s..." % (show1.title, show2.title))
    fig, (ax1, ax2) = plt.subplots(1, 2, **_subplot_args(show1.episode_count + show2.episode_count))
    st = fig.suptitle(_format_compare_title(show1, show2), fontsize=_TITLE_SIZE)
    st.set_y(0.97)
    ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
    _setup(show1, fig, ax1)
    _setup(show2, fig, ax2)
    _plot(show1, fig, ax1, False)
    _plot(show2, fig, ax2, False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    fname = "{show1}--VS--{show2}".format(show1=show1.slug, show2=show2.slug)
    _savefig(fname)
    logging.info("Done!")

def _format_compare_season_title(show1, season1, show2, season2):
    if (show1.slug == show2.slug):
        return "{title}: season {s1} VS season {s2}".format(
            title=show1.title,
            s1=season1.number,
            s2=season2.number)
    else:
        return "{t1}, season {s1} VS {t2}, season {s2}".format(
            t1=show1.title,
            s1=season1.number,
            t2=show2.title,
            s2=season2.number)


def plot_two_seasons(show1, season1, show2, season2):
    logging.info("Plotting %s season %d VS %s season %d..." % (show1.title, season1.number, show2.title, season2.number))
    fig, (ax1, ax2) = plt.subplots(1, 2, **_subplot_args(season1.episode_count + season2.episode_count))
    st = fig.suptitle(_format_compare_season_title(show1, season1, show2, season2), fontsize=_TITLE_SIZE)
    st.set_y(0.97)
    ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
    _setup_season(show1, season1, fig, ax1)
    _setup_season(show2, season2, fig, ax2)
    _plot_season(show1, season1, fig, ax1, False)
    _plot_season(show2, season2, fig, ax2, False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    fname = "{show1}-season-{season1}--VS--{show2}-season-{season2}".format(
        show1=show1.slug,
        season1=season1.number,
        show2=show2.slug,
        season2=season2.number)
    _savefig(fname)
    logging.info("Done!")


def _get_season(show, idx_str):
    return show.season_list[int(idx_str) - 1]


if __name__ == "__main__":

    # setup
    LoggerConfig()
    dbclient = DbClient()


    argc = len(sys.argv)
    if (argc < 2):
        print("Usage: python -m plot.graph <TITLE> [<SEASON>]")
        raise SystemExit(1)

    elif (argc == 2):
        # Single show mode
        show1 = dbclient.get_show(sys.argv[1])
        plot_one_show(show1)
    elif (argc == 3):
        if (sys.argv[2].isdigit()):
            # Single season mode
            show1 = dbclient.get_show(sys.argv[1])
            plot_one_season(show1, _get_season(show1, sys.argv[2]))
        else:
            # Two show mode
            show1 = dbclient.get_show(sys.argv[1])
            show2 = dbclient.get_show(sys.argv[2])
            plot_two_shows(show1, show2)
    else:
        if (sys.argv[3].isdigit()):
            # Two seasons from the same show mode
            show1 = dbclient.get_show(sys.argv[1])
            plot_two_seasons(show1, _get_season(show1, sys.argv[2]), show1, _get_season(show1, sys.argv[3]))
        else:
            # Two seasons from different show modes
            show1 = dbclient.get_show(sys.argv[1])
            show2 = dbclient.get_show(sys.argv[3])
            plot_two_seasons(show1, _get_season(show1, sys.argv[2]), show2, _get_season(show2, sys.argv[4]))





