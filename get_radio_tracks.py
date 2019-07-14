import requests
import json
from bs4 import BeautifulSoup

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
    link = a['href']
    return link.split('?load_more=')[1] # return the part of the string after '?load_more='


def get_tracks_from_load_more(load_more_param, deezer_base_url):
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

    response = requests.get(deezer_base_url + '/music/recently-played/', params=params)

    soup = BeautifulSoup(response.text, 'html.parser')
    tracks = get_tracks_from_soup(soup)

    next_page = soup.find('li', {'class': 'playlist-track-container ondemand-track'})['data-loadmoreurl']

    return tracks, next_page.split('?load_more=')[1]


def get_tracks(deezer_base_url, num_pages=50):

    response = requests.get(deezer_base_url + '/music/recently-played/')
    soup = BeautifulSoup(response.text, 'html.parser')


    ALL_TRACKS = None

    # set up initial page
    ALL_TRACKS = get_tracks_from_soup(soup)
    next_page = get_load_more_param_from_soup(soup)


    # run additional pages
    for x in range(1, num_pages):
        print('page', x + 1)
        tracks, next_page = get_tracks_from_load_more(next_page, deezer_base_url)
        ALL_TRACKS = ALL_TRACKS + tracks

    flattened_tracks = [t[0] + ' ' + t[1] for t in ALL_TRACKS]

    print(flattened_tracks)
    print(len(flattened_tracks), 'total')
    flattened_tracks = list(set(flattened_tracks))
    print(len(flattened_tracks), 'unique')

    return flattened_tracks

if __name__ == '__main__':
    get_tracks('https://thefox.iheart.com', 5)
