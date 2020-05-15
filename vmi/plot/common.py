import unidecode

import matplotlib.pyplot as plt

from pathlib import Path


class Constants:
    BACKGROUND = 'black'
    MIDDLEGROUND = 'gray'
    FOREGROUND = 'white'

    TITLE_SIZE = 20
    SUBTITLE_SIZE = TITLE_SIZE - 4
    LABEL_SIZE = SUBTITLE_SIZE - 3

    SPLINE_K = 2

    COLORS = [
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

    CLOUD_OUTPUT_DIR = "output/clouds/"
    GRAPH_OUTPUT_DIR = "output/graphs/"
    DIRECTOR_OUTPUT_DIR = "output/directors/"


class Formatters:
    @staticmethod
    def format_show_title(show):
        return "{title} - ({rating}/10)".format(
            title=show.title, rating=show.rating)

    @staticmethod
    def format_episode_label(episode):
        return "{label} - ({rating}/10)".format(
            title=show.title, rating=show.rating)

    @staticmethod
    def format_episode_title(episode):
        return "{label} - {title} ({score}/10)".format(
            label=episode.label,
            title=unidecode.unidecode(episode.title),
            score=episode.score)

    @staticmethod
    def format_season_title(show, season, insights):
        return "{title}, season {number} ({rating:.2f}/10)".format(
            title=show.title,
            number=season.number,
            rating=insights.avg_episode_rating)


class Saver:
    @staticmethod
    def savefig(dpath, fname):
        # ensure this directory exists.
        Path(dpath).mkdir(parents=True, exist_ok=True)
        plt.savefig(dpath + fname, bbox_inches="tight")
