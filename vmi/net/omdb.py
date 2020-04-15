import requests
import json
import sys
import os

from model.episode import Episode
from model.show import Show

_BASE_OMDB_URL = "http://www.omdbapi.com/?t={title}&type=series&apikey={api_key}"

class OmdbShowData:
	def __init__(self):
		self.season_count = 0
		self.imdb_id = ""
		self.imdb_rating = 0
		self.title = ""

class OmdbApiClient:
	def __init__(self):
		apikey = os.getenv("OMDB_API_KEY")
		if not apikey:
			print("Must set env variable OMDB_API_KEY")
			raise SystemExit(1)
		self.apikey = apikey

	# Fetch info for a show from OMDB. Raise error if response does not
	# come back.
	def _get_show_data_json(self, title):
		response = requests.request("GET", _BASE_OMDB_URL.format(
			title=title,
			api_key=self.apikey))

		if not response.text:
			print("Error getting info for show '{title}'".format(title=title))
			raise SystemExit(1)

		show_json = json.loads(response.text)

		# quick error check for sanity
		if show_json["Response"] == "False":
			print("Error getting info for show '{title}': {error}".format(
				title=title,
				error=show_json["Error"]))
			raise SystemExit(1)

		return show_json

	def get_show_data(self, title):
		print (title)
		show_info_json = self._get_show_data_json(title)
		data = OmdbShowData()
		data.season_count = int(show_info_json["totalSeasons"])
		data.imdb_id = show_info_json["imdbID"]
		data.imdb_rating = show_info_json["imdbRating"]
		data.title = show_info_json["Title"]
		return data


# for manual module testing only
if __name__ == "__main__":
	if (len(sys.argv)) < 2:
		print("Usage: python -m net.omdb <TITLE>")
		raise SystemExit(1)

	scraper = OmdbApiClient()
	# show_json = scraper.get_show_data(sys.argv[1])
	# print json.dumps(show_json, indent=2)
	handle = scraper.get_show_data(sys.argv[1])
	print handle
