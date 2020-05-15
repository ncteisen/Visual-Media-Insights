class Episode:
    def __init__(self, index, season, number, title, score, imdb_id):
        # overall episode index.
        self.index = index
        # integer season from which this episode was from.
        self.season = season
        # episode number within its season.
        self.number = number
        # episode title.
        self.title = title
        # imdb episode rating
        self.score = score
        # imdb id for this episode
        self.imdb_id = imdb_id
        # short label for the episode
        self.label = "{season:02d}x{number:02d}".format(
            season=season, number=number)

    def __str__(self):
        return "{label}: {title}".format(label=self.label, title=self.title)
