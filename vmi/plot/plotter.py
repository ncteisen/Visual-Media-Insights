import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from pathlib import Path
import logging
from insights.show import ShowInsights
from insights.season import SeasonInsights
import unidecode

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
        return "{title} - ({rating}/10)".format(title=show.title, rating=show.rating)


    def _format_season_title(self, show, season, insights):
        return "{title}, season {number} ({rating:.2f}/10)".format(
            title=show.title, 
            number=season.number, 
            rating=insights.avg_episode_rating)


    def _setup_season(self, show, season, fig, ax):

        # Set background
        ax.set_facecolor(_BACKGROUND)

        # Set colors to cycle for each season
        # TODO, not needed.
        ax.set_prop_cycle(color=_COLORS)

        # Title
        insights = SeasonInsights(season)
        ax.set_title(self._format_season_title(show, season, insights), fontsize=_SUBTITLE_SIZE)

        # Labels
        x_label = "%d episodes" % season.episode_count
        ax.set_xlabel(x_label, fontsize=_LABEL_SIZE)


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
        self._format_footnote_episodes(ax, insights)

        # Ticks
        ax.set_xticks(range(1, len(xlabels) + 1))
        ax.set_xticklabels(xlabels, rotation=90)

        if save:
            path = "../img/single/" + show.slug
            plt.savefig(path, bbox_inches="tight")

    def _plot_season(self, show, season, fig, ax, save = False):

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
        self._format_footnote_episodes(ax, insights)

        # Ticks
        ax.set_xticks(range(1, len(xlabels) + 1))
        ax.set_xticklabels(xlabels, rotation=90)

        if save:
            path = "../img/season/single/" + show.slug + "-season-" + str(season.number)
            plt.savefig(path, bbox_inches="tight")


    def _format_compare_title(self, show1, show2):
        return "{t1} VS {t2}".format(t1=show1.title, t2=show2.title)


    def _format_best_episode(self, episode):
        return "Best:    {label} - {title} ({score}/10)".format(
            label=episode.label,
            title=unidecode.unidecode(episode.title),
            score=episode.score)


    def _format_worst_episode(self, episode):
        return "Worst:  {label} - {title} ({score}/10)".format(
            label=episode.label,
            title=unidecode.unidecode(episode.title),
            score=episode.score)

    def _format_footnote_episodes(self, ax, insights):
        best = insights.best_episode
        ax.annotate(self._format_best_episode(best), (0,0), (0, -80), 
            xycoords='axes fraction', 
            textcoords='offset points', 
            va='top', 
            fontsize=_LABEL_SIZE)
        worst = insights.worst_episode
        ax.annotate(self._format_worst_episode(worst), (0,0), (0, -100), 
            xycoords='axes fraction', 
            textcoords='offset points', 
            va='top', 
            fontsize=_LABEL_SIZE)


    def plot_one_show(self, show):
        logging.info("Plotting %s..." % show.title)
        fig, ax = plt.subplots(**self._subplot_args(show.episode_count))
        ax.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup(show, fig, ax)
        self._plot(show, fig, ax, True)
        logging.info("Done!")

    def plot_one_season(self, show, season):
        logging.info("Plotting season %d for %s..." % (season.number, show.title))
        fig, ax = plt.subplots(**self._subplot_args(season.episode_count))
        ax.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup_season(show, season, fig, ax)
        self._plot_season(show, season, fig, ax, True)
        logging.info("Done!")


    def plot_two_shows(self, show1, show2):
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
        plt.savefig(path, bbox_inches="tight")
        logging.info("Done!")

    def _format_compare_season_title(self, show1, season1, show2, season2):
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


    def plot_two_seasons(self, show1, season1, show2, season2):
        logging.info("Plotting %s season %d VS %s season %d..." % (show1.title, season1.number, show2.title, season2.number))
        fig, (ax1, ax2) = plt.subplots(1, 2, **self._subplot_args(season1.episode_count + season2.episode_count))
        st = fig.suptitle(self._format_compare_season_title(show1, season1, show2, season2), fontsize=_TITLE_SIZE)
        st.set_y(0.97)
        ax1.set_ylabel("episode score", fontsize=_LABEL_SIZE)
        self._setup_season(show1, season1, fig, ax1)
        self._setup_season(show2, season2, fig, ax2)
        self._plot_season(show1, season1, fig, ax1, False)
        self._plot_season(show2, season2, fig, ax2, False)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        path = "../img/season/compare/{show1}-season-{season1}--VS--{show2}-season-{season2}".format(
            show1=show1.slug,
            season1=season1.number,
            show2=show2.slug,
            season2=season2.number)
        plt.savefig(path, bbox_inches="tight")
        logging.info("Done!")





