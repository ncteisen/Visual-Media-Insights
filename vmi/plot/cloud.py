import logging
import re
import sys
import unidecode

import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

from db.db import DbClient
from insights.show import ShowInsights
from insights.season import SeasonInsights
from model.episode import Episode
from model.season import Season
from model.show import Show
from net.net import Net
from plot.common import Constants, Formatters, Saver
from util.logger import LoggerConfig

_CUSTOM_STOPWORDS = ["show", "book", "series", "season", "character",
    "episode", "story", "seasons", "episodes", "characters",
    "books", "hbo", "will", "time"]

_ALL_STOPWORDS = list(STOPWORDS) + _CUSTOM_STOPWORDS

_CLOUD_OUTPUT_DIR = "../output/clouds/"

def _get_corpus(review_list):
    corpus = []
    for review in review_list:
        corpus += re.sub("[^\w]", " ",  review.title.lower()).split()
        corpus += re.sub("[^\w]", " ",  review.body.lower()).split()
    return corpus


def _get_wordcloud(review_list, extra_stopwords):
    logging.info("Creating wordcloud...")
    corpus = _get_corpus(review_list)
    return WordCloud(width=1000, height=1000, 
                    background_color=Constants.FOREGROUND, 
                    stopwords=set(_ALL_STOPWORDS + extra_stopwords), 
                    min_font_size=Constants.LABEL_SIZE).generate(" ".join(corpus))


def make_wordcloud_plot(show, title, best, worst, fname):
    logging.info("Making wordcloud for %s..." % show.title)
    net = Net()

    extra_stopwords = re.sub("[^\w]", " ",  show.title.lower()).split()
    best_wordcloud = _get_wordcloud(net.get_reviews(best.imdb_id), extra_stopwords)
    worst_wordcloud = _get_wordcloud(net.get_reviews(worst.imdb_id), extra_stopwords)
      

    logging.info("Plotting...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12), facecolor=None)
    st = fig.suptitle(title, fontsize=Constants.TITLE_SIZE)
    st.set_y(0.97)
                     
    ax1.set_title(Formatters.format_episode_title(best), fontsize=Constants.SUBTITLE_SIZE)
    ax1.imshow(best_wordcloud) 
    ax1.axis("off") 

    ax2.set_title(Formatters.format_episode_title(worst), fontsize=Constants.SUBTITLE_SIZE)
    ax2.imshow(worst_wordcloud) 
    ax2.axis("off") 

    plt.subplots_adjust(top=0.85)
    plt.tight_layout(pad=0) 
    Saver.savefig(_CLOUD_OUTPUT_DIR, fname)
    logging.info("Done!")


if __name__ == "__main__":

    # setup
    LoggerConfig()
    dbclient = DbClient()
    net = Net()


    argc = len(sys.argv)
    if (argc < 2):
        print("Usage: python -m plot.cloud <TITLE> [<SEASON>]")
        raise SystemExit(1)
    
    show = dbclient.get_show(sys.argv[1])
    if (argc == 2):
        # one show
        insights = ShowInsights(show)
        title = Formatters.format_show_title(show)
        best = insights.best_episode
        worst = insights.worst_episode
        fname = show.slug
    else:
        # one season
        season = show.season_list[int(sys.argv[2]) - 1]
        insights = SeasonInsights(season)
        title = Formatters.format_season_title(show, season, insights)
        best = insights.best_episode
        worst = insights.worst_episode
        fname = show.slug + "-season-" + str(season.number)

    make_wordcloud_plot(show, title, best, worst, fname)

