import requests
import sys
import logging
from bs4 import BeautifulSoup as Soup

from model.show import ShowMetadata

_BASE_IMDB_URL = "https://www.imdb.com/title/{imdb_id}/episodes?season={season}"

class ImdbEpisodeData:
	def __init__(self):
		self.index = None
		self.season = None
		self.number = None
		self.title = None
		self.score = None

class ImdbSeasonData:
	def __init__(self):
		self.episode_list = []

class ImdbShowData:
	def __init__(self):
		self.season_list = []

class ImdbScraper:
	def __init__(self):
		self.episode_index = None

	def _scrape_episode(self, div, season_number):
		div = div.find('div', {'class': 'info'})

		title = div.find('a', {'itemprop': 'name'}).text

		number = int(div.find('meta', {'itemprop': 'episodeNumber'}).attrs.get('content', '0'))
		if number == 0:
			logging.error("IMDB scraper encountered episode number=None")
			return None
		
		score_div = div.find('span', {'class': 'ipl-rating-star__rating'})
		if not score_div:
			logging.error("IMDB scraper encountered episode score_div=None")
			return None
		
		score = float(score_div.text)
		if score == 0: 
			logging.error("IMDB scraper encountered episode score=None")
			return None

		episode_data = ImdbEpisodeData()
		episode_data.season = season_number
		episode_data.index = self.episode_index
		episode_data.number = number
		episode_data.title = title
		episode_data.score = score

		self.episode_index += 1
		return episode_data


	def _scrape_season(self, show_metadata, season_number):
		season_data = ImdbSeasonData()

		season_url = _BASE_IMDB_URL.format(imdb_id=show_metadata.imdb_id, season=season_number)
		content = requests.get(season_url)
		soup = Soup(content.text, features="html.parser")

		for div in soup.find_all('div', {'class': 'list_item'}):
			episode_data = self._scrape_episode(div, season_number)
			if (episode_data):
				season_data.episode_list.append(episode_data)
		return season_data

	# Fetch episode info for a given show metadata from IMDB.
	def scrape_show(self, show_metadata):
		self.episode_index = 1

		show_data = ImdbShowData()
		for season_number in range(1, show_metadata.season_count + 1):
			season_data = self._scrape_season(show_metadata, season_number)
			show_data.season_list.append(season_data)
		return show_data


# module testing only
if __name__ == "__main__":
	# print("Usage: python -m net.imdb")
	scraper = ImdbScraper()
	show_metadata = ShowMetadata("Arrested Development", "arrested", 8.7, "tt0367279", 3)
	show = scraper.scrape_show(show_metadata)
	print str(show)
