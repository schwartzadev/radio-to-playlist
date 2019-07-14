import requests
import json
from bs4 import BeautifulSoup

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


config = load_config()


response = requests.get(config['deezer_base_url'] + '/music/recently-played/')
soup = BeautifulSoup(response.text, 'html.parser')


def get_tracks_from_soup(soup):
    """
    returns a 2d list of track information from an iheartradio soup in the format:
    [
        ...
        [track_name, track_artist],
        ...
    ]
    """
    tracks_list = []
    figcaptions = soup.find_all('figcaption')

    for track in figcaptions:
        song_info = [a.text for a in track.find_all('a')]
        tracks_list.append(song_info)

    return tracks_list


def get_load_more_param_from_soup(soup):
    """
    gets the parameter that lies on the current page and points to the next page of tracks
    this only works for the initial page (not subsequent pages -- see the get_tracks_from_load_more method)
    """
    a = soup.find('a', {'class': 'station-custom-button large load-more'})
    link = config['deezer_base_url'] + a['href']
    return link.split('?load_more=')[1] # return the part of the string after '?load_more='


def get_tracks_from_load_more(load_more_param):
    """
    returns the tracks and the next page parameter, given the current page parameter
    this only works for pages that are NOT the initial page
    """
    params = (
        ('load_more', load_more_param),
        ('viewname', 'undefined'),
        ('limit', '10'),
        ('requestCount', 1),
    )

    response = requests.get(config['deezer_base_url'] + '/music/recently-played/', params=params)

    soup = BeautifulSoup(response.text, 'html.parser')
    tracks = get_tracks_from_soup(soup)

    next_page = soup.find('li', {'class': 'playlist-track-container ondemand-track'})['data-loadmoreurl']
    
    return tracks, next_page.split('?load_more=')[1]


def add_song(song_id):
    """
    add a song to the playlist
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
        ('access_token', ACCESS_TOKEN),
    )
    r = requests.get('https://api.deezer.com/search', params=params)
    
    song_id = json.loads(r.text)['data'][0]['id']
    return song_id



def add_tracks_to_playlist(tracks_list):
    total_tracks = len(tracks_list) + 1 # 1 indexed for the count
    count = 1
    for t in tracks_list:
        try:
            song_id = get_deezer_song_id(t)
            add_song(song_id)
            print('[' + str(count) + '/' + str(total_tracks) + ']', 'added', t, song_id)
        except:
            print('[' + str(count) + '/' + str(total_tracks) + ']', 'error for', t, song_id)
        count = count + 1


ALL_TRACKS = None

# set up initial page
ALL_TRACKS = get_tracks_from_soup(soup)
next_page = get_load_more_param_from_soup(soup)


# run additional pages
for x in range(1, 172):
    print('page', x + 1)
    tracks, next_page = get_tracks_from_load_more(next_page)
    ALL_TRACKS = ALL_TRACKS + tracks

flattened_tracks = [t[0] + ' ' + t[1] for t in ALL_TRACKS]

print(flattened_tracks)
print(len(flattened_tracks), 'total')
flattened_tracks = list(set(flattened_tracks)) # rm duplicates
print(len(flattened_tracks), 'unique')


import pdb
pdb.set_trace()

# add to Deezer
add_tracks_to_playlist(flattened_tracks)
