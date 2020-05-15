class DirectorMetadata:
    def __init__(self, imdb_id, name, slug, movie_metadata_list):
        # imdb id for the director.
        self.imdb_id = imdb_id
        # director name.
        self.name = name
        # director slug
        self.slug = slug
        # metadata of movies this director has directed
        self.movie_metadata_list = movie_metadata_list


class Director:
    def __init__(self, director_metadata, movie_list):
        # director name.
        self.name = director_metadata.name
        # director slug
        self.slug = director_metadata.slug
        # movies this director has directed
        self.movie_list = movie_list
