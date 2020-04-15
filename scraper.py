""" Scraper module """

"""
This module is responsible for scraping OMDB and IMDB then returning model
versions of shows and episodes. This could eventually be replaced by a
database client.
"""

import requests
import json
import sys
from bs4 import BeautifulSoup as Soup

from episode import Episode
from show import Show

_BASE_OMDB_URL = "http://www.omdbapi.com/?t={title}&type=series&apikey={api_key}"
_BASE_IMDB_URL = "https://www.imdb.com/title/{imdb_id}/episodes?season={season}"

class Scraper:
	def __init__(self, apikey):
		self.apikey = apikey

	# Fetch info for a show from OMDB. Raise error if response does not
	# come back.
	def _get_omdb_info(self, title):
		response = requests.request("GET", _BASE_OMDB_URL.format(
			title=title,
			api_key=self.apikey))
		show_json = json.loads(response.text)

		# quick error check for sanity
		if show_json["Response"] == "False":
			print("Error getting info for show '{title}': {error}".format(
				title=title,
				error=show_json["Error"]))
			raise SystemExit(1)

		return show_json



	# Fetch episode info for a given show from IMDB.
	# from: https://github.com/federicocalendino/binging-stonks
	def _scrape_episodes(self, imdb_id, seasons, show):
		episodes = []
		index = 1
		for season_number in range(1, seasons + 1):
			season_url = _BASE_IMDB_URL.format(imdb_id=imdb_id, season=season_number)

			content = requests.get(season_url)
			soup = Soup(content.text, features="html.parser")

			for div in soup.find_all('div', {'class': 'list_item'}):
				div = div.find('div', {'class': 'info'})

				episode_title = div.find('a', {'itemprop': 'name'}).text
				episode_number = int(div.find('meta', {'itemprop': 'episodeNumber'}).attrs.get('content', '0'))

				if episode_number == 0:
					continue

				episode_score_div = div.find('span', {'class': 'ipl-rating-star__rating'})

				if not episode_score_div:
					continue

				episode_score = float(episode_score_div.text)

				if episode_score == 0:
					continue

				episode = Episode(
					index=index,
					season=season_number,
					number=episode_number,
					title=episode_title,
					score=episode_score,
				)

				index += 1
				show.add_episode(season_number, episode)


	# Based on title, attempts to read and parse all episode info about a
	# particular show. Raises an system exist if we encounter any errors.
	def parse_show(self, title):

		omdb_show_info = self._get_omdb_info(title)
		num_seasons = int(omdb_show_info["totalSeasons"])
		imdb_id = omdb_show_info["imdbID"]
		imdb_rating = omdb_show_info["imdbRating"]

		show = Show(title, imdb_rating, num_seasons)
		self._scrape_episodes(imdb_id, num_seasons, show)
		return show




# module testing only
if __name__ == "__main__":
	if (len(sys.argv)) < 3:
		print("Usage: python scraper.py '<API_KEY>' '<TITLE>' '<FNAME>'")
		raise SystemExit(1)

	scraper = Scraper(sys.argv[1])
	show = scraper.parse_show(sys.argv[2])
	with open(sys.argv[3], 'wb') as f:
 		pickle.dump(show, f)
