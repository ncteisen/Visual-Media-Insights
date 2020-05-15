from bs4 import BeautifulSoup as Soup

from vmi.net.imdb import ImdbScraper


# sanity test for The Wire Season 1
def test_the_wire_season_one(datadir):
    scraper = ImdbScraper()
    scraper.episode_index = 0
    soup = Soup(open(datadir / 'the-wire-season-one.htm'), 'html.parser')
    season_data = scraper.scrape_season_soup(soup, 1)

# sanity test for Martin Scorsese


def test_martin_scorsese(datadir):
    scraper = ImdbScraper()
    soup = Soup(open(datadir / 'martin-scorsese.htm'), 'html.parser')
    director_data = scraper.scrape_director_soup(soup)
    assert(director_data.name == "Martin Scorsese")
    assert(len(director_data.movie_metadata_list) > 0)

# sanity test for Martin Scorsese


def test_martin_scorsese_search(datadir):
    scraper = ImdbScraper()
    soup = Soup(open(datadir / 'martin-scorsese-search.htm'), 'html.parser')
    imdb_id = scraper.scrape_name_soup(soup)
    assert(imdb_id == "nm0000217")

# regression test for missing box office and runtime info


def test_satoshi_kon(datadir):
    scraper = ImdbScraper()
    soup = Soup(open(datadir / 'satoshi-kon.htm'), 'html.parser')
    director_data = scraper.scrape_director_soup(soup)
    assert(director_data.name == "Satoshi Kon")
    assert(len(director_data.movie_metadata_list) > 0)
