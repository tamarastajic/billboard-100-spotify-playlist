from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ~~~~~~~~~~~~~~ NECESSARY SPOTIFY DATA ~~~~~~~~~~~~~~
# Input your own data!
SPOTIFY_CLIENT_ID = YOUR SPOTIFY CLIENT ID
SPOTIFY_CLIENT_SECRET = YOUR SPOTIFY CLIENT SECRET

# ~~~~~~~~~~~~~~ Billboard 100 URL ~~~~~~~~~~~~~~
billboard_url = "https://www.billboard.com/charts/hot-100/"

# -------------------- Custom DATE --------------------
date = input("Which date do you want to travel to? Make sure to input it in a  YYYY-MM-DD format: ")
billboard_url += date

# -------------------- Acquring Data from URL --------------------
response = requests.get(billboard_url)
webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")

# Acquiring all songs
raw_all_songs = soup.find_all(name="h3", id="title-of-a-story", class_="a-no-trucate")
all_songs = []
for song in raw_all_songs:
    new_song = song.getText().strip()
    for i, letter in enumerate(new_song):
        if (letter == "(" or letter == "/" or letter == "-") and i != 0:
            new_song = new_song[:i]
            break
    all_songs.append(new_song)

# Acquiring all artists
raw_all_artists = soup.find_all(name ="li", class_ = "lrv-u-width-100p")
all_artists = []
for i, artist in enumerate(raw_all_artists):
    if i % 2 == 0:
        all_artists.append(artist.select_one("span").getText().strip())

# -------------------- Spotipy API --------------------

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"))

user_id = sp.current_user()["id"]

# Find URI of All Songs
uri_all_songs = []
for i, song in enumerate(all_songs):
        song_uri = sp.search(f"track:{song} artist:{all_artists[i]}")
        try:
                song_uri = song_uri["tracks"]["items"][0]["uri"]
        except:
                print(f"Couldn't find {song} - {all_artists[i]} on Spotify.")
                continue
        uri_all_songs.append(song_uri)

# Create a Playlist
playlist = sp.user_playlist_create(user=user_id,
                        name=f"Top 100 {date}",
                        public=False,
                        collaborative=False,
                        description=f"A playist of the top 100 songs on {date}")

# Add Tracks to Playlist
playlist_id = playlist["id"]
sp.user_playlist_add_tracks(user_id, playlist_id, uri_all_songs)

