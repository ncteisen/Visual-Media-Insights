import requests
import sys
import logging

from bs4 import BeautifulSoup as Soup
from decimal import Decimal
from re import sub

from vmi.model.show import ShowMetadata

_BASE_IMDB_SHOW_URL = "https://www.imdb.com/title/{imdb_id}/episodes?season={season}"
_BASE_IMDB_DIRECTOR_URL_ = "https://www.imdb.com/name/{imdb_id}"
_BASE_IMDB_EPISODE_REVIEW_URL = "https://www.imdb.com/title/{imdb_id}/reviews"
_BASE_IMDB_MOVIE_URL = "https://www.imdb.com/title/{imdb_id}"

# All this info can be retrieved from the episode list page on IMDB.
class ImdbEpisodeData:
	def __init__(self):
		self.index = None
		self.season = None
		self.number = None
		self.title = None
		self.score = None
		self.imdb_id = None

class ImdbSeasonData:
	def __init__(self):
		self.episode_list = []

class ImdbShowData:
	def __init__(self):
		self.season_list = []

class ImdbReviewData:
	def __init__(self):
		self.title = None
		self.body = None

class ImdbEpisodeReviewsData:
	def __init__(self):
		self.review_list = []

# This information can be found in the movie list under a director page on IMDB.
class ImdbMovieMetadata:
	def __init__(self):
		self.name = None
		self.imdb_id = None
		self.year = None

class ImdbDirectorData:
	def __init__(self):
		self.name = None
		self.movie_metadata_list = []

class ImdbMovieData:
	def __init__(self):
		self.budget = None
		self.opening_weekend = None
		self.us_boxoffice = None
		self.worldwide_boxoffice = None
		self.runtime = None
		self.genre_list = []

class ImdbScraper:
	def __init__(self):
		self.episode_index = None

	def _scrape_episode(self, div, season_number):
		div = div.find('div', {'class': 'info'})

		name_div = div.find('a', {'itemprop': 'name'})
		title = name_div.text
		imdb_id = name_div['href'].split('/')[2]

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
		episode_data.imdb_id = imdb_id

		self.episode_index += 1
		return episode_data


	def _scrape_season(self, show_metadata, season_number):
		season_data = ImdbSeasonData()

		season_url = _BASE_IMDB_SHOW_URL.format(imdb_id=show_metadata.imdb_id, season=season_number)
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

	def _scrape_one_review(self, div):
		review_data = ImdbReviewData()
		review_data.title = div.find('a', {'class': 'title'}).text
		review_data.body = div.find('div', {'class': 'text'}).text
		return review_data


	def scrape_top_reviews(self, imdb_id):
		episode_reviews_url = _BASE_IMDB_EPISODE_REVIEW_URL.format(imdb_id=imdb_id)
		content = requests.get(episode_reviews_url)
		soup = Soup(content.text, features="html.parser")
		review_data = ImdbEpisodeReviewsData()
		for div in soup.find_all('div', {'class': 'imdb-user-review'}):
			review_data.review_list.append(self._scrape_one_review(div))
		return review_data


	def _scrape_movie_metadata(self, div):
		# Title is the hyperlink
		title = div.find('a').text
		year = div.find('span', {'class': 'year_column'}).text
		# Non feature films have more info after the title. We filter on that.
		post = div.find('b').next_sibling
		if not post.isspace():
			return None
		
		movie_metadata = ImdbMovieMetadata()
		movie_metadata.title = title
		movie_metadata.imdb_id = div['id'][len("director-"):]
		movie_metadata.year = int(year.strip().split('/')[0])
		return movie_metadata


	def scrape_director(self, imdb_id):
		director_url = _BASE_IMDB_DIRECTOR_URL_.format(imdb_id=imdb_id)
		content = requests.get(director_url)
		soup = Soup(content.text, features="html.parser")
		director_data = ImdbDirectorData()
		name_overview_div = soup.find('div', {'class': 'name-overview-widget'})
		name_div = name_overview_div.find('span', {'class': 'itemprop'})
		director_data.name = name_div.text
		for div in soup.find_all('div', {'class': 'filmo-row'}):
			if (div['id'].startswith('director')):
				movie_metadata = self._scrape_movie_metadata(div)
				if (movie_metadata):
					director_data.movie_metadata_list.append(movie_metadata)
		return director_data


	def _parse_num(self, money):
		return Decimal(sub(r'[^\d.]', '', money))


	def scrape_movie(self, imdb_id):
		movie_url = _BASE_IMDB_MOVIE_URL.format(imdb_id=imdb_id)
		content = requests.get(movie_url)
		soup = Soup(content.text, features="html.parser")
		movie_data = ImdbMovieData()


		# scrape box office info
		iterator = soup.find("h3", string="Box Office")
		if (iterator):
			for _ in range(4):
				iterator = iterator.findNext('div')
				h4 = iterator.find('h4')
				if not h4: continue
				if "Budget" in h4.text:
					movie_data.budget = self._parse_num(h4.next_sibling)
				if "Opening Weekend USA" in h4.text:
					movie_data.opening_weekend = self._parse_num(h4.next_sibling)
				if "Gross USA" in h4.text:
					movie_data.us_boxoffice = self._parse_num(h4.next_sibling)
				if "Cumulative Worldwide Gross" in h4.text:
					movie_data.worldwide_boxoffice = self._parse_num(h4.next_sibling)


		# scrape runtime
		iterator = soup.find("h3", string="Technical Specs")
		iterator = iterator.findNext('div')
		time = iterator.find('time')
		movie_data.runtime = int(time.text[:-3])


		# scrape rating count
		rating_count_span = soup.find('span', {'itemprop': 'ratingCount'})
		if (rating_count_span):
			movie_data.rating_count = self._parse_num(rating_count_span.text)


		# scrape genres
		genre_h4 = soup.find("h4", string="Genres:")
		genre_span = genre_h4.parent
		if (genre_span):
			for a in genre_span.find_all('a'):
				movie_data.genre_list.append(a.text.strip())


		return movie_data



# module testing only
if __name__ == "__main__":
	# print("Usage: python -m net.imdb")
	scraper = ImdbScraper()
	# director = scraper.scrape_director("nm0000217")
	movie_data = scraper.scrape_movie("tt0082910")
	print (movie_data.runtime)
