import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from lyricsgenius import Genius
from utils import *
import csv
import time

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")


client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = Genius(GENIUS_TOKEN, verbose=False, remove_section_headers=True, retries=4, timeout=15)
seen_songs = set()


def add_songs_to_csv(csv_path, playlists_file_path, age_appropriate):
    """
    Csv file should already be created.
    Kids should be either a 0 (not for kids) or a 1 (for kids)
    """

    with open(playlists_file_path, "r") as f:
        for playlist_link in f:
            playlist_id = get_playlist_id(playlist_link)
            results = sp.playlist_tracks(playlist_id)
            items = results["items"]
            # Get all the results before you you start getting lyrics
            while results["next"]:
                results = sp.next(results)
                items.extend(results["items"])

            for item in items:
                track = item["track"]

                if not track:
                    continue

                track_name = track["name"]
                artist = track["artists"][0]["name"]
                song = None
                if (track_name, artist) in seen_songs:
                    print(f"{track_name} by {artist} already in csv")
                    continue

                try:
                    time.sleep(3)
                    song = genius.search_song(track_name, artist)
                except (TimeoutError):
                    time.sleep(30) # we miss one song but that should be ok
                    continue

                if not song: # lyric genius couldn't find the song
                    continue

                lyrics = unique_lyrics(song.lyrics)

                # make sure all the lyrics are in english
                if not is_english(lyrics):
                    continue

                seen_songs.add((track_name, artist))
                with open(csv_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([artist, track_name, lyrics, age_appropriate])

path = "data/adultsTryTwo.csv"
start = time.time()
if not os.path.exists(path):
    create_csv(path, ["Artist", "TrackName", "Lyrics", "AgeAppropriate"])
else:
    with open(path, "r") as f:
        reader = csv.reader(f)
        next(reader) # skip over the header
        for line in reader:
            artist = line[0]
            track_name = line[1]
            seen_songs.add((track_name, artist))
    print("Going to append to existing csv file, added seen songs")

add_songs_to_csv(path, "dataset_creation/adults_playlists.txt", 0)
# print("Now starting the kids songs...")
# add_songs_to_csv(path, "dataset_creation/kids_playlists.txt", 1)
end = time.time()

songs_added = 0
with open(path, "r", newline="") as f:
    reader = csv.reader(f)
    songs_added = sum(1 for _ in reader)

print(f"Took {(end-start):.3f} seconds to get {songs_added-2} songs")
