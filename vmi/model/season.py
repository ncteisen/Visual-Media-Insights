class Season:
    def __init__(self, number, episode_list):
        # season number.
        self.number = number
        # list of episode_list in the season.
        self.episode_list = episode_list
        # number of episodes in the season.
        self.episode_count = len(episode_list)

    def __str__(self):
        return "Season[season_number={number}, episode_count={episode_count}]".format(
            number=self.number, episode_count=self.episode_count)
