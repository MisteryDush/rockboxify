import configparser
import os
from difflib import SequenceMatcher

from spotdl.download.downloader import Downloader
from spotdl.utils import spotify
from spotdl.types.song import Song
from song import Song as DwnlSong
from mutagen.easyid3 import EasyID3
from playlist import Playlist
import requests
import glob
import tekore as tk
import shutil

auth = "8c348c85dc414a49948f3271af0331c3:9f1034ea825246759a5d8c0c48ebc85d"
data = {
    "grant_type": f"client_credentials",
    "client_id": "8c348c85dc414a49948f3271af0331c3",
    "client_secret": "9f1034ea825246759a5d8c0c48ebc85d"
}
headers = {
    "Content-Type": f"application/x-www-form-urlencoded"
}

dwnld = Downloader()


def get_playlists():
    playlists = []
    for path in glob.glob(f"{local_path}*"):
        temp_playlist = Playlist(path.split("\\")[-1], path)
        playlists.append(temp_playlist)
    return playlists


def get_downloaded_songs():
    playlists = get_playlists()
    for playlist in playlists:
        for file in glob.glob(f"{playlist.path}/*.mp3"):
            audio = EasyID3(file)
            title = audio.get('title', ['Unknown Title'])[0]
            artist = audio.get('artist', ['Unknown Artist'])[0]
            album = audio.get('album', ['Unknown Album'])[0]
            playlist.add_song(DwnlSong(title, artist, album))
    return playlists


def get_missing_playlists(spotify_playlists, local_playlists):
    local_playlists_dict = {playlist.name: playlist for playlist in local_playlists}
    spotify_playlists_dict = {playlist.name: playlist for playlist in spotify_playlists}

    missing_locally = [spotify_playlists_dict[name] for name in spotify_playlists_dict if
                       name not in local_playlists_dict]

    return missing_locally


def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


def create_missing_playlists(missing_playlists):
    for playlist in missing_playlists:
        print(playlist)
        print(f"Transferring playlist {playlist.name}")
        dir_name = f"{local_path}{playlist.name}"
        os.makedirs(dir_name)
        i = 0
        not_found_songs = []
        for song in playlist.songs:
            temp = Song.from_url(song.link)
            try:
                result = dwnld.download_song(temp)
                shutil.move(f"C:/Users/Ikram Arifdjanov/Desktop/rockboxify/{sanitize_filename(result[0].name)}.mp3",
                            f"{dir_name}/{sanitize_filename(result[0].name)}.mp3")
                i += 1
            except FileNotFoundError:
                song.lookup_error = True
                not_found_songs.append(song)
        for song in not_found_songs:
            print(song.title)
        write_missing_songs_to_file(not_found_songs, playlist.name)
        print(f"{len(not_found_songs)} {'song' if len(not_found_songs) == 1 else 'songs'} not found")
        print(f"Created playlist '{playlist.name}' with {i} songs")


def write_missing_songs_to_file(missing_songs, playlist_name):
    try:
        with open(f"playlists_info/{playlist_name}_missing.txt", mode="w", encoding="utf-8") as file:
            for song in missing_songs:
                file.write(f"{song.title},{song.artist},{song.album},{1 if song.lookup_error else 0}\n")
    except FileNotFoundError:
        os.makedirs(f"playlists_info")
        write_missing_songs_to_file(missing_songs, playlist_name)


def read_specific_line(filepath, line_number):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for current_line_number, line in enumerate(file, start=1):
                if current_line_number == line_number:
                    return line.strip()  # Remove any extra whitespace, including '\n'
    except FileNotFoundError:
        return ''
    return ''  # Return None if the line number does not exist


def download_missing_songs(missing_songs, playlist):
    local_dir_name = f"{local_path}{playlist.name}"
    for i in range(0, len(missing_songs)):
        line_content = read_specific_line(f'playlists_info/{playlist.name}_missing.txt', i + 1).split(',')
        if missing_songs[i].lookup_error or line_content[-1] == '1':
            print(f'Skipping {missing_songs[i].title}: LookupError')
            missing_songs[i].lookup_error = True
            continue
        else:
            temp = Song.from_url(missing_songs[i].link)
            temp.name = sanitize_filename(temp.name)
            try:
                result = dwnld.download_song(temp)
                base_directory = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_directory, f"{sanitize_filename(result[0].name)}.mp3")
                shutil.move(file_path,
                            f"{local_dir_name}/{sanitize_filename(result[0].name)}.mp3")
                playlist.songs.append(missing_songs[i])
            except FileNotFoundError:
                missing_songs[i].lookup_error = True


def check_missing_songs(spotify_playlists, playlists):
    playlists_sorted = sorted(playlists, key=lambda p: p.name)
    spotify_playlists_sorted = sorted(spotify_playlists, key=lambda p: p.name)
    for i in range(0, len(playlists_sorted)):
        local_playlist = playlists_sorted[i]
        spotify_playlist = spotify_playlists_sorted[i]
        missing_songs = find_missing_songs(local_playlist.songs, spotify_playlist.songs)
        download_missing_songs(missing_songs, local_playlist)
        write_missing_songs_to_file(find_missing_songs(local_playlist.songs, spotify_playlist.songs),
                                    spotify_playlist.name)


def similar(a, b, threshold=0.6):
    return SequenceMatcher(None, a, b).ratio() >= threshold


def find_missing_songs(local_songs, spotify_songs):
    local_song_set = [(sanitize_filename(song.title), song.artist.lower(), song.album.lower()) for song in local_songs]

    missing_songs = []
    for spotify_song in spotify_songs:
        spotify_title = sanitize_filename(spotify_song.title)
        spotify_artist = spotify_song.artist.lower()
        spotify_album = spotify_song.album.lower()
        match_found = any(
            similar(sanitize_filename(spotify_title), sanitize_filename(local_title)) and similar(
                sanitize_filename(spotify_artist), sanitize_filename(local_artist.split('/')[0])) and similar(
                sanitize_filename(spotify_album),
                sanitize_filename(local_album)) for
            local_title, local_artist, local_album in local_song_set)
        if not match_found:
            missing_songs.append(spotify_song)

    return missing_songs


def get_creds():
    global client_id, client_secret, local_path
    config = configparser.ConfigParser()

    if not os.path.exists('config.cfg'):
        raise FileNotFoundError("The configuration file 'config.cfg' does not exist.")

    config.read('config.cfg')

    client_id = config['DEFAULT']['client_id']
    client_secret = config['DEFAULT']['client_secret']
    local_path = config['DEFAULT']['path_to_local_playlists']


def main():
    get_creds()
    playlists = get_downloaded_songs()
    spotify.SpotifyClient.init(client_id, client_secret)
    r = requests.post(f"https://accounts.spotify.com/api/token", data=data, headers=headers)
    access_token = r.json()["access_token"]
    tekore = tk.Spotify(access_token)
    r = requests.get("https://api.spotify.com/v1/users/wz6bqsb235vsx9lhb75uhydij/playlists",
                     headers={"Authorization": f"Bearer {access_token}"})
    spotify_playlists = []
    for item in r.json()['items']:
        spotify_playlists.append(Playlist(item['name'], link=item['external_urls']['spotify']))

    for playlist in spotify_playlists:
        i = 0
        first_items = tekore.playlist_items(playlist.link.split('/')[-1])
        for item in tekore.all_items(first_items):
            playlist.add_song(DwnlSong(item.track.name, item.track.artists[0].name, item.track.album.name,
                                       link=f"https://open.spotify.com/track/{item.track.uri.split(':')[-1]}"))
            i += 1

    missing_playlists = get_missing_playlists(spotify_playlists, playlists)

    create_missing_playlists(missing_playlists)

    check_missing_songs(spotify_playlists, playlists)


if __name__ == '__main__':
    client_id = ''
    client_secret = ''
    local_path = ''
    main()

'''                              `-:/+++++++/++:-.                                          
                            .odNMMMMMMMMMMMMMNmdo-`                                      
                           +mMMNmdhhhhhhhhhdmNMMMNd/`                                    
                          sMMMmhyyyyyyyyyyyyyyhmNMMMh-                                   
                         +MMMdyyyyyyyhhhhdddddddmMMMMN/                                  
                        `NMMmyyyyyymNNMMNNNmmmmmmmNNMMMy`                                
                        :MMMhyyyyyNMMMho+//:-.....-:omMMd-                               
                    ```:mMMNhyyyyhMMMh+::::-        `:sNMN:                              
                 -oyhdmMMMMmhyyyyhMMNyy+::::---------::yMMm                              
                +MMMMNNNMMMdhyyyyhMMNyyyso/::::::://+oshMMM`                             
                NMMNhyyyMMMhhyyyyyNMMmyyyyyyssssyyyyyyymMMd                              
                MMMdyyyhMMNhhyyyyyhNMMNdyyyyyyyyyyyhdmMMMN-                              
                MMMdhhhdMMNhhhyyyyyymMMMMNmmmmmmNNMMMMMMN.                               
                MMMhhhhdMMNhhhyyyyyyyhdmNNNMMNNNmmdhhdMMd                                
               `MMMhhhhdMMNhhhhyyyyyyyyyyyyyyyyyyyyyydMMM.                               
               .MMMhhhhdMMNhhhhyyyyyyyyyyyyyyyyyyyyyydMMM:                               
               .MMNhhhhdMMNhhhhhyyyyyyyyyyyyyyyyyyyyhhMMM+                               
               -MMNhhhhdMMNhhhhhyyyyyyyyyyyyyyyyyyyyhdMMM/                               
               -MMMhhhhdMMNhhhhhhhyyyyyyyyyyyyyyyyyhhdMMM-                               
               `MMMhhhhhMMNhhhhhhhhhhyyyyyyyyyyyhhhhhmMMN                                
                hMMmhhhhMMNhhhhhhhhhhhhhhhhhhhhhhhhhhNMMy                                
                :MMMNmddMMMhhhhhhhhhhddddhhhhhhhhhhhdMMM/                                
                 :hNMMMMMMMdhhhhhhhhdMMMMMMNNNNNdhhhNMMN`                                
                   .-/+oMMMmhhhhhhhhmMMmyhMMMddhhhhdMMMy                                 
                        hMMNhhhhhhhhmMMd :MMMhhhhhhdMMM+                                 
                        sMMNhhhhhhhhNMMm .MMMdhhhhhdMMN.                                 
                        /MMMdhhhhhhdMMM+  oNMMNNNNNMMm:                                  
                        `dMMMNmmmNNMMMh`   -syyyyhhy/`                                   
                         `/hmNNNNNmdh/`                                                  
                            `.---..`
                            '''
