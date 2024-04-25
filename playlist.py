from song import Song


class Playlist:

    def __init__(self, name: str, path='', link=''):
        self.name = name.strip().lower()
        self.path = path
        self.songs = []
        self.link = link
        if self.link != '' and path == '':
            self.is_local = False
        else:
            self.is_local = True

    def add_song(self, song: Song):
        self.songs.append(song)

    def __str__(self):
        return f"Playlist {self.name} {'at ' + self.path if self.is_local else 'from Spotify'}"

    def __repr__(self):
        return self.__str__()
