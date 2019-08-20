import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from spotipy.util import prompt_for_user_token
from spotipy import util
from tools.whosampled_scrape import *
import config as cfg

#==[ link types ]===================#
URI = 'uri'
HTTP = 'http'
EMBED = 'embed'

#==[ source types ]=================#
PLAYLIST = 'playlist'
ALBUM = 'album'
ARTIST = 'artist'
SONG = 'song'
CURRENT_SONG = 'current_song'

#==[ output types ]=================#
CREATE_ONLY = 'w'
APPEND_ONLY = 'a'
APPEND_OR_CREATE = 'a+'

def get_token(scope='playlist-modify-public'):
    token = util.prompt_for_user_token(cfg.username,
                                       scope,
                                       client_id=cfg.client,
                                       client_secret=cfg.secret,
                                       redirect_uri=cfg.redirect)
    return token


def get_spotify_ids(whosampled_playlist, sp_session):
    id_list = []
    unfound_list = []
    for track in whosampled_playlist:
        sub_list = []
        artist = track['artist'].lower()
        result = sp_session.search(track['title'], limit=50)['tracks']['items']

        for entry in result:
            if entry['artists'][0]['name'].lower() == artist:
                sub_list.append(entry['id'])
                break

        if sub_list: # hit
            id_list.append(sub_list[0])
        else:        # no hit
            unfound_list.append((track['title'] + ' by ' + artist))

    location_rate = 1 - len(unfound_list) / len(whosampled_playlist)
    return {'ids': id_list, 'unfound': unfound_list, 'rate': location_rate}


def create_and_populate(username, new_playlist_name, spotify_dict, sp):
    playlist = sp.user_playlist_create(cfg.username, new_playlist_name)

    newest_id = sp.user_playlists(cfg.username)['items'][0][
        'id']  # get ID of playlist just created
    sp.user_playlist_add_tracks(username, newest_id, spotify_dict['ids'],
                                None)  #populate playlist with all samples


def populate_output(output_type, output_name, content, sp_session):
    playlist_id = 0
    if output_type == APPEND_ONLY or output_type == APPEND_OR_CREATE:
        # search for user playlist where output_name == playlist name
        raise NotImplemented("Functionality not supported yet")

    if output_type == CREATE_ONLY and playlist_id == 0:
        playlist = sp_session.user_playlist_create(cfg.username, output_name)
        print(f'populate_output, playlist => {playlist}')
        # get created playlist_id
        playlist_id = sp_session.user_playlists(cfg.username)['items'][0]['id']

    # FIXME: find out what this magic None param corresponds to from spotipy docs
    sp_session.user_playlist_add_tracks(cfg.username, playlist_id, content['ids'],
                                None)  # populate playlist with all samples


def get_new_sample_playlist(playlist_uri, new_playlist_name, user):
    token = get_token('playlist-modify-public')
    sp_session = spotipy.Spotify(auth=token)

    playlist_id = get_identfier_from_reference_type(reference=playlist_uri, reference_type=URI)
    source_songs = get_source_list_from_type(playlist_id, PLAYLIST, sp_session)
    new_playlist_tracks = get_sample_data(source_songs)

    print('\nChecking Spotify for Samples:\n')
    for track in new_playlist_tracks:
        print(track['title'] + ' by ' + track['artist'])
    spotify_dict = get_spotify_ids(new_playlist_tracks, sp_session)

    output_type = CREATE_ONLY
    output_name = new_playlist_name
    new_playlist = populate_output(output_type=output_type, output_name=output_name,
                                   content=spotify_dict, sp_session=sp_session)
    # new_playlist = create_and_populate(user, new_playlist_name, spotify_dict, sp_session)
    print(f'New playlist "{new_playlist_name}" created!')


def generate_description(source, samples):
    """
    Gives some information on the playlist.

    """
    # sample_title, sample_artist, direction, source_artist, source_title
    song_template = '\n    {0}, by {1}. {2} by {3} in {4}'
    unfound = str.join('\n', spot_dict['unfound'])
    rate = round(spot_dict['rate'], 3)
    description_template = f"""
This playlist was generated from the {source_type}: {source_name}.
    For more information, head to https://github.com/qzdl/samplify

Percentage Matched:
    {rate}

Songs with no match:
    {unfound}

Song Info:
    """
    # sp2.user_playlist_change_details(cfg.username, playlist_id, name=new_playlist_name, public=None, collaborative=None,description=description)
    return summary


def parse_output_option(output_option, output_name):
    """
    provides the logic for output options:
    CREATE_ONLY:

    """
    pass


def format_source_result(results):
    og_tracks = []
    for entry in results['tracks']['items']:
        artists = [prop['name'] for prop in entry['track']['artists']]
        og_tracks.append({
            'artist': artists,
            'track': entry['track']['name'].replace('Instrumental', '')
        })
    return og_tracks


def get_sample_data(source_songs):
    new_playlist_tracks = get_whosampled_playlist(source_songs)
    return new_playlist_tracks


def get_source_list_from_type(source_id, source_type, sp_session):
    """
    Parses out type (song|album|playlist) from link
    """
    source_list = {}
    if source_type == PLAYLIST:
        results = sp_session.user_playlist(cfg.username, source_id)
    if source_type == ALBUM:
        source_list = {}
    if source_type == SONG:
        source_list = {}
    if source_type == CURRENT_SONG:
        source_list = {}
    return format_source_result(results)


def get_identfier_from_reference_type(reference, reference_type):
    """
    extracts necessary identifier from reference
    (url|uri|embed|scan_image)
    TODO: handle url
    TODO: handle embed
    TODO: handle scan_image
    """
    if reference_type == URI:
        return reference.split(':')[2]
    raise Exception(f'Reference type {reference_type} not supported')


def samplify(direction, reference, reference_type, source_type, output_name, output_type=CREATE_ONLY):
    """
    The most general endpoint for interacting with samplify

    direction:
        specify (sampled_by|samples)
    reference:
        link to identify the content. e.g. spotify:playlist:23sdf098y23kj
    reference_type:
        the type of the reference given, e.g. uri
    source_type:
        specify (album|song|current_song|playlist)
    output_name:
        name of output playlist
    output_type:
        (append_only|create_only|append_or_create)
        default=create_only
    """
    token = get_token('playlist-modify-public')
    sp_session = spotipy.Spotify(auth=token)

    identifier = get_identfier_from_reference_type(reference, reference_type)
    source_songs = get_source_list_from_type(identifier, source_type, sp_session=sp_session)
    sample_data = get_sample_data(source_songs)

    spotify_dict = get_spotify_ids(sample_data, sp_session)
    new_playlist = populate_output(output_type=output_type, output_name=output_name,
                                   content=spotify_dict, sp_session=sp_session)
    print(f'Created playlist {output_name}')


def main():
    playlist_uri = input(
        'Please enter the Spotify URI of your playlist. \nThis can be found by clicking "Share" on your playlist and then selecting "Copy Spotify URI":\n>>> '
    )
    new_playlist_name = input(
        'Please enter the name of your new sample playlist\n>>> ')
    get_new_sample_playlist(playlist_uri, new_playlist_name, cfg.username)


# main()
