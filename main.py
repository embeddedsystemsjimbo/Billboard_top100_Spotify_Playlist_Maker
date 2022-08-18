import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
from logo import logo
import os

SPOTIPY_CLIENT_ID = os.environ.get("spotipy_client_id")
SPOTIPY_CLIENT_SECRET = os.environ.get("spotipy_client_secret")
SPOTIPY_REDIRECT_URI = os.environ.get("spotipy_redirect_uri")



def get_billboard_top_100(billboard_date):

    """
     Scrap https://www.billboard.com/charts/hot-100/ for top 100 songs on a given data
        Parameter:
            billboard_date (str): Date to search for billboard top 100 songs given in YYYY-MM-DD format.
        Return:
            artist_song_list (list/tuple/str): Returns list of two value tuples where first tuple position is the artist
                                                name and the second tuple position in the song.
    """

    response = requests.get(f"https://www.billboard.com/charts/hot-100/{billboard_date}/")
    billboard_website = response.text
    soup = BeautifulSoup(billboard_website, "html.parser")

    # get top artist 1
    top_artist = soup.find(class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max"
                                  " u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block"
                                  " a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"
                                  " u-font-size-20@tablet").getText().strip()

    # get top song 1
    top_song = soup.find(class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                "u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125"
                                " u-line-height-normal@mobile-max a-truncate-ellipsis "
                                "u-max-width-245 u-max-width-230@tablet-only"
                                " u-letter-spacing-0028@tablet").getText().strip()

    # get other artist 2-100
    artists = [artist.getText().strip() for artist in
               soup.find_all(class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max "
                                    "u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block "
                                    "a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")]

    # get other songs from 2-100
    songs = [song.getText().strip() for song in
             soup.find_all(class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                  "lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 "
                                  "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 "
                                  "u-max-width-230@tablet-only")]

    artists.insert(0, top_artist)
    songs.insert(0, top_song)

    artist_song_list = list(zip(artist_description_filter(artists), songs))

    return artist_song_list


def artist_description_filter(artist_list):

    """
        Filters artist descriptions to one primary artist where there exist more than one artist associated with a song.
            Parameter:
                artist_list (list_str): List of artist descriptions.
            Return:
                filtered_artist_list (list_str): Returns list of artist where there is only one primary artist in each
                                                 string.
    """

    filtered_artist_list = []

    # remove all text after first connecting word "Featuring", "&" or "With.
    for artist_description in artist_list:

        if "Featuring" in artist_description:

            index = artist_description.index("Featuring")
            filtered_artist_list.append(artist_description[:index].strip())

        elif "&" in artist_description:

            index = artist_description.index("&")
            filtered_artist_list.append(artist_description[:index].strip())

        elif "With" in artist_description:

            index = artist_description.index("With")
            filtered_artist_list.append(artist_description[:index].strip())

        else:
            filtered_artist_list.append(artist_description)

    return filtered_artist_list


def get_song_uri(artist, song):

    try:
        # search spotify for song id
        search_result = sp.search(q=f"artist:{artist} track:{song}", type="track", limit=1)
        return search_result["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f'The song:"{song}" from artist:"{artist}" is not currently available')


scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))


print(logo)

date = input("Which year do you want to travel to ? Type the date in this format YYYY-MM-DD ")

song_uri_list = [get_song_uri(item[0], item[1]) for item in get_billboard_top_100(date)
                 if get_song_uri(item[0], item[1]) is not None]

# create new playlist
playlist = sp.user_playlist_create(user=sp.me()["id"], name=f"Billboard Memories Playlist from {date}", public=False)

# get ID of newly created playlist
playlist_id = playlist["id"]

# add billboard top 100 list to newly crated Spotify playlist
sp.playlist_add_items(playlist_id=playlist_id, items=song_uri_list)

# get external url link to spotify playlist
external_url = sp.playlist(playlist_id=playlist_id)

print(external_url["external_urls"]["spotify"])

