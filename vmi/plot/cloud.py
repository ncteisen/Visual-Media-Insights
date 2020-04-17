import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS 
import pandas as pd 
import numpy as np
from pathlib import Path
import logging
from insights.show import ShowInsights
from insights.season import SeasonInsights
from model.review import Review
import unidecode
import re
import sys

from model.episode import Episode
from model.season import Season
from model.show import Show

from db.db import DbClient
from net.net import Net

_BACKGROUND = 'black'
_MIDDLEGROUND = 'gray'
_FOREGROUND = 'white'

_TITLE_SIZE = 20
_SUBTITLE_SIZE = _TITLE_SIZE - 4
_LABEL_SIZE = _SUBTITLE_SIZE - 3

_CUSTOM_STOPWORDS = ["show", "book", "series", "season", "character",
    "episode", "story", "seasons", "episodes", "characters",
    "books", "hbo", "will", "time"]

def _get_corpus(review_list):
    corpus = []
    for review in review_list:
        corpus += re.sub("[^\w]", " ",  review.title.lower()).split()
        corpus += re.sub("[^\w]", " ",  review.body.lower()).split()
    return corpus


def _get_wordcloud(review_list):
    corpus = _get_corpus(review_list)
    return WordCloud(width=1000, height=1000, 
                    background_color=_FOREGROUND, 
                    stopwords=set(list(STOPWORDS) + _CUSTOM_STOPWORDS), 
                    min_font_size=_LABEL_SIZE).generate(" ".join(corpus))


def _format_show_title(show):
    return "{title} - ({rating}/10)".format(title=show.title, rating=show.rating)


def _format_episode_title(episode):
    return "{label} - ({rating}/10)".format(title=show.title, rating=show.rating)


def _format_episode_title(episode):
    return "{label} - {title} ({score}/10)".format(
        label=episode.label,
        title=unidecode.unidecode(episode.title),
        score=episode.score)


def make_wordcloud_plot(show):
    insights = ShowInsights(show)
    net = Net()
    
    best = insights.best_episode
    worst = insights.worst_episode
    best_wordcloud = _get_wordcloud(net.get_reviews(best.imdb_id))
    worst_wordcloud = _get_wordcloud(net.get_reviews(worst.imdb_id))
      

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12), facecolor=None)
    st = fig.suptitle(_format_show_title(show), fontsize=_TITLE_SIZE)
    st.set_y(0.97)
                     
    ax1.set_title(_format_episode_title(best), fontsize=_SUBTITLE_SIZE)
    ax1.imshow(best_wordcloud) 
    ax1.axis("off") 

    ax2.set_title(_format_episode_title(worst), fontsize=_SUBTITLE_SIZE)
    ax2.imshow(worst_wordcloud) 
    ax2.axis("off") 

    plt.subplots_adjust(top=0.85)
    plt.tight_layout(pad=0) 
    path = "../img/cloud/" + show.slug
    plt.savefig(path, bbox_inches="tight")



# module testing only
if __name__ == "__main__":
    dbclient = DbClient()
    net = Net()
    show = dbclient.get_show(sys.argv[1])
    make_wordcloud_plot(show)