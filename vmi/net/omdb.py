import requests
import json
import sys
import os

_BASE_SERIES_OMDB_URL = "http://www.omdbapi.com/?t={title}&type=series&apikey={api_key}"
_BASE_MOVIE_OMDB_URL = "http://www.omdbapi.com/?i={imdb_id}&type=series&apikey={api_key}"


class OmdbShowData:
    def __init__(self):
        self.season_count = None
        self.imdb_id = None
        self.imdb_rating = None
        self.title = None


class OmdbMovieData:
    def __init__(self):
        self.imdb_id = None
        self.title = None
        self.year = None
        self.imdb_rating = None
        self.box_office = None


class OmdbApiClient:
    def __init__(self):
        apikey = os.getenv("OMDB_API_KEY")
        if not apikey:
            print("""Must set env variable OMDB_API_KEY!

Go to http://www.omdbapi.com/apikey.aspx to get a free API key. Then set it:
$ export OMDB_API_KEY=<YOUR_KEY>
""")
            raise SystemExit(1)
        self.apikey = apikey

    # Fetch info for a show from OMDB. Raise error if response does not
    # come back.
    def _get_show_metadata_json(self, title):
        response = requests.request("GET", _BASE_SERIES_OMDB_URL.format(
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

    def get_show_metadata(self, title):
        show_info_json = self._get_show_metadata_json(title)
        data = OmdbShowData()
        data.season_count = int(show_info_json["totalSeasons"])
        data.imdb_id = show_info_json["imdbID"]
        data.imdb_rating = show_info_json["imdbRating"]
        data.title = show_info_json["Title"]
        return data

    # Fetch info for a movie from OMDB. Raise error if response does not
    # come back.

    def _get_movie_data_json(self, imdb_id):
        response = requests.request("GET", _BASE_MOVIE_OMDB_URL.format(
            imdb_id=imdb_id,
            api_key=self.apikey))

        if not response.text:
            print(
                "Error getting info for movie '{imdb_id}'".format(
                    imdb_id=imdb_id))
            raise SystemExit(1)

        movie_json = json.loads(response.text)

        # quick error check for sanity
        if movie_json["Response"] == "False":
            print("Error getting info for movie '{imdb_id}': {error}".format(
                imdb_id=imdb_id,
                error=movie_json["Error"]))
            raise SystemExit(1)

        return movie_json

    def get_movie_data(self, movie_metadata):
        movie_info_json = self._get_movie_data_json(movie_metadata.imdb_id)
        data = OmdbMovieData()
        data.imdb_id = movie_metadata.imdb_id
        data.title = movie_info_json["Title"]
        data.year = movie_info_json["Year"]
        data.imdb_rating = float(movie_info_json["imdbRating"])
        if "BoxOffice" in movie_info_json and movie_info_json["BoxOffice"] != 'N/A':
            data.box_office = int(
                movie_info_json["BoxOffice"].replace(
                    "$", "").replace(
                    ",", ""))
        return data


# for manual module testing only
if __name__ == "__main__":
    if (len(sys.argv)) < 2:
        print("Usage: python -m net.omdb <TITLE>")
        raise SystemExit(1)

    scraper = OmdbApiClient()
