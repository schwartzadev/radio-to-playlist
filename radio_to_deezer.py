import requests
import json
from bs4 import BeautifulSoup

from get_radio_tracks import get_tracks

"""
07/11/19
Andrew Schwartz
Saves an iHeartRadio station's latest played tracks to a Deezer playlist
"""

import sys, getopt

def load_config(filename):
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(filename, 'does not exist. create a config file from the instructions in the README.\nquitting...')
        quit(1)
    return config


def get_arguments(argv):
    pages_count = 10
    playlist_id = None
    access_token = None
    base_url = None

    config_file_name = 'config.json'
    use_file_config = True

    help_string = """
         -m    uses [m]anual credentials (ignores any config file)
         -h    shows [h]elp
         -c <[c]onfig file> -h <help>
         -n <[n]umber of pages>
         --playlist_id <deezer playlist id>
         --base_url <the https://XXXXXX.iheart.com URL for a radio station>
         --access_token <a deezer access token from the deezer API>
     """

    try:
        opts, args = getopt.getopt(argv, "hmc:n:", ["playlist_id=", "base_url=", "access_token="])
    except getopt.GetoptError:
        print(help_string)
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt == "-c":
            config_file_name = arg
        elif opt == "-n":
            try:
                pages_count = int(arg)
            except ValueError:
                print('-n value must be an integer')
                print('quitting...')
                sys.exit()
        elif opt == "--playlist_id":
            playlist_id = arg
        elif opt == "--base_url":
            base_url = arg
        elif opt == "--access_token":
            access_token = arg
        elif opt == "-m":
            use_file_config = False


    if use_file_config:
        config = load_config(config_file_name)
    else:
        config = {'deezer_access_token': None, 'deezer_base_url': None, 'deezer_playlist_id': None}

    if playlist_id is not None:
        config['deezer_playlist_id'] = playlist_id
    if base_url is not None:
        config['deezer_base_url'] = base_url
    if access_token is not None:
        config['deezer_access_token'] = access_token

    config_values = [v for k,v in config.items()]

    if any([a is None for a in config_values]):
        # if any of the values in the config are None
        print('invalid config:', config)
        print('quitting...')
        sys.exit()

    return config['deezer_access_token'], config['deezer_base_url'], config['deezer_playlist_id'], pages_count


def add_songs(song_id):
    """
    song_id: a string of comma separated song ids
    add a list of songs to the playlist
    """
    querystring = {"songs": song_id, "access_token": access_token}
    r = requests.request(
        "POST",
        "https://api.deezer.com/playlist/{0}/tracks".format(playlist_id),
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
        ('access_token', access_token),
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


access_token, base_url, playlist_id, pages_count = get_arguments(sys.argv[1:])

flattened_tracks = get_tracks(base_url, pages_count)

add_tracks_to_playlist(flattened_tracks)
