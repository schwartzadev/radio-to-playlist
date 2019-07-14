import requests
import json
from bs4 import BeautifulSoup

from get_radio_tracks import get_tracks

"""
07/11/19
Andrew Schwartz
Saves an iHeartRadio station's latest played tracks to a Deezer playlist
"""

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print('config.json does not exist. create a config file from the instructions in the README.\nquitting...')
        quit(1)
    return config


def add_songs(song_id):
    """
    song_id: a string of comma separated song ids
    add a list of songs to the playlist
    """
    querystring = {"songs": song_id, "access_token": config['deezer_access_token']}
    r = requests.request(
        "POST",
        "https://api.deezer.com/playlist/{0}/tracks".format(config['deezer_playlist_id']),
        params=querystring
    )
    if r.text == 'true':
        return True
    else:
        print('adding song', song_id, 'failed:', r.text)
        return False


def get_deezer_song_id(query):
    """
    call the Deezer API to search for the track, returning the highest rank result
    """
    params = (
        ('q', query),
        ('order', 'RANKING'),
        ('access_token', config['deezer_access_token']),
    )
    r = requests.get('https://api.deezer.com/search', params=params)
    
    song_id = json.loads(r.text)['data'][0]['id']
    return song_id


def add_tracks_to_playlist(tracks_list):
    total_tracks = len(tracks_list)
    count = 1
    song_ids = []
    for t in tracks_list:
        try:
            song_id = get_deezer_song_id(t)
            song_ids.append(song_id)
            print('[' + str(count) + '/' + str(total_tracks) + ']', 'added', t, song_id)
        except:
            print('[' + str(count) + '/' + str(total_tracks) + ']', 'could not find', t, song_id)
        count = count + 1
    song_ids_as_string = ','.join(str(sid) for sid in song_ids)
    add_songs(song_ids_as_string)


config = load_config()

flattened_tracks = get_tracks(config['deezer_base_url'], 2)

add_tracks_to_playlist(flattened_tracks)
