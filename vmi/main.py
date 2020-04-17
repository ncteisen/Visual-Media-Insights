import sys
import logging

from db.db import DbClient
from net.net import Net
from plot.plotter import Plotter
from plot.cloud import make_wordcloud
from insights.show import ShowInsights

logging.basicConfig(format='%(asctime)s - %(filename)20s: %(message)s');

root = logging.getLogger()
root.setLevel(logging.INFO)

def _get_season(show, idx_str):
	return show.season_list[int(idx_str) - 1]

dbclient = DbClient()
plotter = Plotter()

argc = len(sys.argv)
if (argc < 2):
	print("Usage: python scraper.py <TITLE> [<TITLE>]")
	raise SystemExit(1)
elif (argc == 2):
	# Single show mode
	show1 = dbclient.get_show(sys.argv[1])
	plotter.plot_one_show(show1)
elif (argc == 3):
	if (sys.argv[2].isdigit()):
		# Single season mode
		show1 = dbclient.get_show(sys.argv[1])
		plotter.plot_one_season(show1, _get_season(show1, sys.argv[2]))
	else:
		# Two show mode
		show1 = dbclient.get_show(sys.argv[1])
		show2 = dbclient.get_show(sys.argv[2])
		plotter.plot_two_shows(show1, show2)
else:
	if (sys.argv[3].isdigit()):
		# Two seasons from the same show mode
		show1 = dbclient.get_show(sys.argv[1])
		plotter.plot_two_seasons(show1, _get_season(show1, sys.argv[2]), show1, _get_season(show1, sys.argv[3]))
	else:
		# Two seasons from different show modes
		show1 = dbclient.get_show(sys.argv[1])
		show2 = dbclient.get_show(sys.argv[3])
		plotter.plot_two_seasons(show1, _get_season(show1, sys.argv[2]), show2, _get_season(show2, sys.argv[4]))

