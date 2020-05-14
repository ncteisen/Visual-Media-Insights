from bs4 import BeautifulSoup as Soup

from vmi.net.imdb import ImdbScraper


# sanity test for Martin Scorsese
def test_martin_scorsese(datadir):
	scraper = ImdbScraper()
	soup = Soup(open(datadir / 'martin-scorsese.htm'), 'html.parser')
	movie_data = scraper.scrape_movie_soup(soup)

# regression test for missing box office and runtime info
def test_satoshi_kon(datadir):
	scraper = ImdbScraper()
	soup = Soup(open(datadir / 'satoshi-kon.htm'), 'html.parser')
	movie_data = scraper.scrape_movie_soup(soup)