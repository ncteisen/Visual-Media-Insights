import requests
import json
import sys
import pickle

from scraper import Scraper
from plotter import Plotter

if (len(sys.argv)) < 3:
	print("Usage: python scraper.py '<API_KEY>' '<TITLE>' '<TITLE>'")
	raise SystemExit(1)

scraper = Scraper(sys.argv[1])
plotter = Plotter();

show1 = scraper.parse_show(sys.argv[2])
show2 = scraper.parse_show(sys.argv[3])

# with open('tmp/simpsons', 'rb') as f:
#     simpsons = pickle.load(f)
# with open('tmp/arrested', 'rb') as f:
#     arrested = pickle.load(f)

plotter.plot_two(show1, show2)
# plotter.plot_one(show1)