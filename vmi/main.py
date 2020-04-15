import sys
import logging

from db.db import DbClient
from plot.plotter import Plotter

logging.basicConfig(format='%(asctime)s - %(filename)20s: %(message)s');

root = logging.getLogger()
root.setLevel(logging.INFO)

if (len(sys.argv)) < 2:
	print("Usage: python scraper.py <TITLE> [<TITLE>]")
	raise SystemExit(1)

dbclient = DbClient()
plotter = Plotter();

show1 = dbclient.get_show(sys.argv[1])

if (len(sys.argv) > 2):
	show2 = dbclient.get_show(sys.argv[2])
	plotter.plot_two(show1, show2)
else:
	plotter.plot_one(show1)