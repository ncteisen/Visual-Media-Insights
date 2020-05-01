import logging
import sys
import unidecode

import matplotlib.pyplot as plt
import numpy as np

from scipy import interpolate

from vmi.db.db import DbClient
from vmi.insights.show import ShowInsights
from vmi.insights.season import SeasonInsights
from vmi.plot.common import Constants, Formatters, Saver
from vmi.util.logger import LoggerConfig

def _subplot_args(episode_count):
    return {
        # TODO(ncteisen): support dynamic height
        "figsize": (10 + 5 * max(episode_count / 25, 1), 10), 
        "dpi": 80, 
        "facecolor": Constants.BACKGROUND,
        "sharey": True
    }


def _setup_season(show, season, fig, ax):

    # Set background
    ax.set_facecolor(Constants.BACKGROUND)

    # Set colors to cycle for each season
    # TODO, not needed.
    ax.set_prop_cycle(color=Constants.COLORS)

    # Title
    insights = SeasonInsights(season)
    ax.set_title(Formatters.format_season_title(show, season, insights), fontsize=Constants.SUBTITLE_SIZE)

    # Labels
    x_label = "%d episodes" % season.episode_count
    ax.set_xlabel(x_label, fontsize=Constants.LABEL_SIZE)


def _setup(show, fig, ax):

    # Set background
    ax.set_facecolor(Constants.BACKGROUND)

    # Set colors to cycle for each season
    ax.set_prop_cycle(color=Constants.COLORS)

    # Title
    ax.set_title(Formatters.format_show_title(show), fontsize=Constants.SUBTITLE_SIZE)

    # Labels
    x_label = "%d episodes" % show.episode_count
    if show.season_count > 1:
        x_label = "{x_label} - {season_count} seasons".format(x_label=x_label, season_count=show.season_count)
    ax.set_xlabel(x_label, fontsize=Constants.LABEL_SIZE)


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

    insights = ShowInsights(show)
    _format_footnote_episodes(ax, insights)

    # Ticks
    ax.set_xticks(range(1, len(xlabels) + 1))
    ax.set_xticklabels(xlabels, rotation=90)

    if save: Saver.savefig(Constants.GRAPH_OUTPUT_DIR, show.slug)

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
        sp_y = interpolate.make_interp_spline(x, y, k=Constants.SPLINE_K)(sp_x)
        ax.plot(sp_x, sp_y)

    # Plots the per season trend
    z = np.polyfit(x, y, deg=1)
    p = np.poly1d(z)
    ax.scatter(x, y)
    ax.plot(x, p(x), color=Constants.MIDDLEGROUND)

    insights = SeasonInsights(season)
    _format_footnote_episodes(ax, insights)

    # Ticks
    ax.set_xticks(range(1, len(xlabels) + 1))
    ax.set_xticklabels(xlabels, rotation=90)

    if save: Saver.savefig(Constants.GRAPH_OUTPUT_DIR, show.slug + "-season-" + str(season.number))


def _format_compare_title(show1, show2):
    return "{t1} VS {t2}".format(t1=show1.title, t2=show2.title)


def _format_best_episode(episode):
    return "Best:    {formatted_title}".format(
        formatted_title=Formatters.format_episode_title(episode))


def _format_worst_episode(episode):
    return "Worst:  {formatted_title}".format(
        formatted_title=Formatters.format_episode_title(episode))

def _format_footnote_episodes(ax, insights):
    best = insights.best_episode
    ax.annotate(_format_best_episode(best), (0,0), (0, -80), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=Constants.LABEL_SIZE)
    worst = insights.worst_episode
    ax.annotate(_format_worst_episode(worst), (0,0), (0, -100), 
        xycoords='axes fraction', 
        textcoords='offset points', 
        va='top', 
        fontsize=Constants.LABEL_SIZE)


def plot_one_show(show):
    logging.info("Plotting %s..." % show.title)
    fig, ax = plt.subplots(**_subplot_args(show.episode_count))
    ax.set_ylabel("episode score", fontsize=Constants.LABEL_SIZE)
    _setup(show, fig, ax)
    _plot(show, fig, ax, True)
    logging.info("Done!")

def plot_one_season(show, season):
    logging.info("Plotting season %d for %s..." % (season.number, show.title))
    fig, ax = plt.subplots(**_subplot_args(season.episode_count))
    ax.set_ylabel("episode score", fontsize=Constants.LABEL_SIZE)
    _setup_season(show, season, fig, ax)
    _plot_season(show, season, fig, ax, True)
    logging.info("Done!")


def plot_two_shows(show1, show2):
    logging.info("Plotting %s VS %s..." % (show1.title, show2.title))
    fig, (ax1, ax2) = plt.subplots(1, 2, **_subplot_args(show1.episode_count + show2.episode_count))
    st = fig.suptitle(_format_compare_title(show1, show2), fontsize=Constants.TITLE_SIZE)
    st.set_y(0.97)
    ax1.set_ylabel("episode score", fontsize=Constants.LABEL_SIZE)
    _setup(show1, fig, ax1)
    _setup(show2, fig, ax2)
    _plot(show1, fig, ax1, False)
    _plot(show2, fig, ax2, False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    fname = "{show1}--VS--{show2}".format(show1=show1.slug, show2=show2.slug)
    Saver.savefig(Constants.GRAPH_OUTPUT_DIR, fname)
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
    st = fig.suptitle(_format_compare_season_title(show1, season1, show2, season2), fontsize=Constants.TITLE_SIZE)
    st.set_y(0.97)
    ax1.set_ylabel("episode score", fontsize=Constants.LABEL_SIZE)
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
    Saver.savefig(Constants.GRAPH_OUTPUT_DIR, fname)
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





