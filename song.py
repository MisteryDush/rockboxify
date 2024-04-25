class Song:
    def __init__(self, title, artist, album, link='', lookup_error=False):
        self.title = title.strip().lower()
        self.artist = artist.strip().lower()
        self.album = album.strip().lower()
        self.link = link
        self.lookup_error = lookup_error
        if self.link != '':
            self.is_local = False
        else:
            self.is_local = True

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def __repr__(self):
        return self.__str__()
