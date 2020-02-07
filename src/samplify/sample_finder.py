import json
from time import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.util import prompt_for_user_token
from spotipy import util
from fuzzywuzzy import fuzz
import objectpath

from samplify.tools.whosampled import Scraper
from samplify.tools.options import Options
from samplify.tools.logger import Logger
from samplify.tools import direction as d

import samplify.config as cfg

# uri => spotify:album:2laBNOqPW85M3js7qCYhKt
# http => https://open.spotify.com/album/2laBNOqPW85M3js7qCYhKt?si=QkZUkYZpSpuT1Xir6z7hGw

class Samplify(object):
    def __init__(self, scope='playlist-modify-public',
                 prompt_for_token=True, verbosity=0, token=None):
        self.verbosity = verbosity
        self.logger = Logger(verbosity=self.verbosity, log_file=f'Samplify-{time()}')
        self.scraper = Scraper(verbosity=self.verbosity)
        self.tokens = []
        if prompt_for_token:
            token = self.get_token(scope)
            self.tokens.append((scope, token))
            self.spotify = spotipy.Spotify(auth=token)

    def samplify(self, options):
        """ The most general endpoint for interacting with samplify

        """
        source_songs = self.get_source_spotify_tracks(options)
        sample_data = self.get_sample_data(source_songs, options.direction)


        spotify_dict = self.get_sample_spotify_tracks(sample_data, options)
        options.output_name, description = self.populate_output(
            options=options,
            sample_tracks=spotify_dict
        )

        self.log(message=f'\n{description}')
        self.log(message=f'Created playlist {options.playlist_name}')
        return self.spotify


    def from_search(self, search_term, content_type,
                    direction=None, output_name=None, output_type=None):
        options = Options()
        result = self.spotify.search(search_term, limit=50)
        self.log(message=f'Searched for "{search_term}"',
                 function='from_search',
                 data=result)
        if not result:
            return None

        # build objectpath query & get first result
        tree_obj = objectpath.Tree(result)
        search_mod = '.album' if options.type_is_album(content_type) else ''
        query = f'$.tracks.items{search_mod}.(name, uri)'
        queried = json.loads(json.dumps(tuple(tree_obj.execute(query))))[0]

        options.parent_name = queried['name']
        reference = queried['uri']

        options.generate(
            reference=reference,
            direction=direction,
            content_type=content_type,
            output_name=output_name,
            output_type=output_type
        )
        return self.samplify(options)

    def current_song(self, direction=None, output_name=None, output_type=None):
        """API for E2E rip of sample data from current song playing"""
        # scope required?
        options = Options()
        options.generate(
            reference=None,
            direction=direction,
            content_type=options.CURRENT_SONG,
            output_name=output_name,
            output_type=output_type
        )
        return self.samplify(options)

    def song(self, reference, direction=None, output_name=None, output_type=None):
        """API for E2E rip of sample data from song"""
        options = Options()
        options.generate(
            reference=reference,
            direction=direction,
            content_type=options.SONG,
            output_name=output_name,
            output_type=output_type
        )
        return self.samplify(options)

    def album(self, reference, direction=None, output_name=None, output_type=None):
        """API for E2E rip of sample data from album"""
        options = Options()
        options.generate(
            reference=reference,
            direction=direction,
            content_type=options.ALBUM,
            output_name=output_name,
            output_type=output_type
        )
        return self.samplify(options)

    def playlist(self, reference, direction=None, output_name=None,
                 output_type=None, username=None):
        options = Options()
        options.generate(
            reference=reference,
            direction=direction,
            content_type=options.PLAYLIST,
            output_name=output_name,
            output_type=output_type,
            username=username
        )
        return self.samplify(options)

    def artist(self, reference):
        pass


    def get_token(self, scope='playlist-modify-public'):
        token = util.prompt_for_user_token(
            cfg.username, scope, client_id=cfg.client,
            client_secret=cfg.secret, redirect_uri=cfg.redirect)
        return token


    def get_source_spotify_tracks(self, options):
        """ Retrieves tracks respecting source_type (song|album|playlist)
            options:
              <Options>
            Returns:
              <list>
        """
        results = []
        track_parser = lambda track: track
        if options.content_type == options.PLAYLIST:
            results = self.spotify.user_playlist(options.username, options.reference)
            track_parser = lambda track: track['track']

        if options.content_type == options.ALBUM:
            results = self.spotify.album(options.reference)

        if options.content_type == options.SONG:
            results.append(self.spotify.track(options.reference))

        if options.content_type == options.CURRENT_SONG:
            results.append(self.spotify.currently_playing())

        return self.format_source_result(results, track_parser, options)

    def format_source_result(self, results, track_parser, options):
        og_tracks = []
        options.parent_name = results['name']
        for entry in results['tracks']['items']:
            track = track_parser(entry)
            artists = [prop['name'] for prop in track['artists']]
            og_tracks.append({
                'artist': artists,
                'track': track['name'].replace('Instrumental', ''),
                'uri': track['uri']
            })
        return og_tracks

    def get_sample_spotify_tracks(self, sample_tracks, options):
        """ Searches spotify for sample tracks
        if options.include_originator, the originator is placed in found_songs
        """
        self.log(message='Checking Spotify for Samples',
                 function='get_sample_spotify_tracks',
                 data=sample_tracks)
        found_songs = []  # matches append {'detail': foo, 'search_query': baz, 'id': bar}
        unfound_list = [] # this is just a one-dimensional list
        # track = og track
        total_sample_count = 0
        for source_track in sample_tracks:
            og_title = source_track['track']
            # direction = { 'Was sampled in ': [{}, ...] }
            originator_used = False
            for direction, tracks in source_track['samples'].items():
                total_sample_count = total_sample_count + len(tracks)
                found_unfound = self.something_parser(tracks, og_title, direction)

                if not originator_used \
                   and direction == d.was_sampled_in:
                    originator_used = True
                    found_songs.append({
                        'detail': 'The originator of sample data',
                        'search_query': 'n/a',
                        'id': source_track['uri']
                    })

                found_songs = found_songs + found_unfound[0]
                unfound_list = unfound_list + found_unfound[1]

                if not originator_used:
                    originator_used = True
                    found_songs.append({
                        'detail': 'The originator of sample data',
                        'search_query': 'n/a',
                        'id': source_track['uri']
                    })
        find_rate = 1 - len(unfound_list) / total_sample_count
        return {'found': found_songs, 'unfound': unfound_list, 'rate': find_rate}

    def something_parser(self, tracks, og_title, direction):
        found_list = []
        unfound_list = []
        for track in tracks:
            sub_list = []
            title = track['title']
            artist = track['artist']
            null = lambda s, ss: s.replace(ss, ' ')
            s_artist = null(null(null(null(null(artist.lower(),
                        '&'), ' feat '), ' feat. '), ' the '), ' and ')
            detail = f'( {og_title} )->-[ {direction} ]->-( {title}, by {artist} )'
            search_query = f'{title} {s_artist}'
            self.log(message=f'Searching spotify with {search_query}',
                    function='get_sample_spotify_tracks',
                    data=f'query: {search_query}\ndetail:{detail}')

            result = self.spotify.search(search_query, limit=10)['tracks']['items']
            for entry in result: # iter search results for first artist fuzzy match
                search_artist = entry['artists'][0]['name'].lower()
                if fuzz.token_set_ratio(search_artist, s_artist) < 90:
                    self.log(
                        message=f'no match for s:{search_query}, r:{entry["name"]}',
                        function=''
                    )
                    continue
                sub_list.append({
                    'detail': detail,
                    'search_query': search_query,
                    'id': entry['id']
                })
                break
            if sub_list: # hit
                found_list.append(sub_list[0])
            else:        # no hit
                unfound_list.append({
                    'detail': detail,
                    'search_query': search_query
                })
        return (found_list, unfound_list)
    def get_sample_data(self, source_songs, direction):
        new_playlist_tracks = self.scraper.get_whosampled_playlist(
            source_songs, direction)
        return new_playlist_tracks


    def populate_output(self, options, sample_tracks):
        playlist_id = 0
        playlist_name = \
            options.output_name if options.output_name \
                                else f'SAMPLIFY: {options.parent_name}'

        options.playlist_name = playlist_name
        description, long_description = self.generate_description(
            sample_data=sample_tracks, options=options)

        if options.output_type == options.APPEND_ONLY or \
           options.output_type == options.APPEND_OR_CREATE:
            # search for user playlist where output_name == playlist name
            raise NotImplemented("Functionality not supported yet")

        if options.output_type == options.CREATE_ONLY and playlist_id == 0:
            # create playlist, then retrieve id

            playlist = self.spotify.user_playlist_create(
                user=options.username, name=playlist_name,
                public=True) # FIXME: allow private playlists
            playlist_id = self.spotify.user_playlists(
                options.username)['items'][0]['id']

        ids = [track['id'] for track in sample_tracks['found']]

        self.spotify.user_playlist_add_tracks(
            options.username, playlist_id, ids, position=None)
        self.spotify.user_playlist_change_details(
            playlist_id=playlist_id,description=description)
        return playlist_name, description

    def generate_description(self, sample_data, options):
        """
        Gives some information on the playlist.
        - Descriptions in spotify are 300 chars
        """
        join = lambda key, sub_key: str.join('''
''', [track[sub_key] for track in sample_data[key]])

        unfound = join('unfound', 'detail')
        u_searches = join('unfound', 'search_query')

        found = join('found', 'detail')
        f_searches = join('found', 'search_query')
        rate = round(sample_data['rate'], 3) * 100

        long_description = f'''
# {options.playlist_name}

This playlist was generated using Samplify.
Github: https://github.com/qzdl/samplify

The {options.content_type}, {options.parent_name}, has been broken down into:
"{[i.lower() for i in options.direction]}"

Percentage Matched: {rate}%

Songs with no match:
{unfound}

==> search terms:
{u_searches}

Sample Info:
{found}

==> search terms:
{f_searches}
        '''
        self.log(message='Description generated successfully',
                 function='generate_description',
                 data=long_description)

        description = f'This playlist was generated using samples found in {options.parent_name}, with Samplify. Github: https://github.com/qzdl/samplify. Found: {rate}%.'
        return description, long_description


    def log(self, **kwargs):
        self.logger.log(**kwargs)
