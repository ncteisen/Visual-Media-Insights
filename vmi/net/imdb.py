import requests
import sys
from bs4 import BeautifulSoup as Soup

from model.episode import Episode
from model.show import Show

_BASE_IMDB_URL = "https://www.imdb.com/title/{imdb_id}/episodes?season={season}"

class ImdbScraper:
	# Fetch episode info for a given show from IMDB.
	# from: https://github.com/federicocalendino/binging-stonks
	def _scrape_episodes(self, show):
		episodes = []
		index = 1
		for season_number in range(1, show.season_count + 1):
			season_url = _BASE_IMDB_URL.format(imdb_id=show.imdb_id, season=season_number)

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


# module testing only
if __name__ == "__main__":
	# print("Usage: python -m net.imdb")
	scraper = ImdbScraper()
	imdb_id = "tt0367279"
	num_seasons = 3
	show = Show("Arrested Development", 8.7, 3)
	scraper._scrape_episodes(imdb_id, num_seasons, show)
	print show
	print show.seasons
