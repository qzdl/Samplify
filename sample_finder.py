import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.util import prompt_for_user_token
from spotipy import util
from fuzzywuzzy import fuzz
from tools.whosampled_scrape import Scraper
from tools import direction as d
import config as cfg
import json
import objectpath

#==[ link types ]===================#
URI = 'uri' # spotify:album:2laBNOqPW85M3js7qCYhKt
HTTP = 'http' # https://open.spotify.com/album/2laBNOqPW85M3js7qCYhKt?si=QkZUkYZpSpuT1Xir6z7hGw

class Options:
    def __init__(self):
       # source types
       self.PLAYLIST = 'playlist'
       self.ALBUM = 'album'
       self.ARTIST = 'artist'
       self.SONG = 'song'
       self.CURRENT_SONG = 'current_song'

       # output types
       self.CREATE_ONLY = 'w'
       self.APPEND_ONLY = 'a'
       self.APPEND_OR_CREATE = 'a+'

    def type_is_playlist(self, content_type):
        return content_type == self.PLAYLIST

    def type_is_album(self, content_type):
        return content_type == self.ALBUM

    def type_is_artist(self, content_type):
        return content_type == self.ALBUM

    def type_is_song(self, content_type):
        return content_type == self.SONG

    def type_is_current_song(self, content_type):
        return content_type == self.CURRENT_SONG

    def generate(self, reference, direction=None, content_type=None, scope=None,
                 output_name=None, output_type=None, username=None):
        """Request-wise options object
        direction:
            specify (sampled_by|samples)
        reference:
            link to identify the content. e.g. spotify:playlist:23sdf098y23kj
        reference_type:
            the type of the reference given, e.g. uri
        content_type:
            specify (album|song|current_song|playlist)
        output_name:
            name of output playlist
        output_type:
            (play|append_only|create_only|append_or_create)
            default=create_only
        """
        self.reference = reference
        self.direction = direction if direction else d.contains_sample_of
        if content_type:
            self.content_type = content_type
        else:
            pass # TODO parse content_type
        self.output_name = output_name
        self.output_type = output_type if output_type else self.CREATE_ONLY
        self.scope = scope
        self.username = username if username else cfg.username


class Samplify:
    def __init__(self, scope='playlist-modify-public',
                 prompt_for_token=True, debug=False, token=None):
        self.scraper = Scraper()
        self.tokens = []
        self.debug = debug
        if prompt_for_token:
            token = self.get_token(scope)
            self.tokens.append((scope, token))
            self.spot = spotipy.Spotify(auth=token)


    def samplify(self, options):
        """ The most general endpoint for interacting with samplify

        """
        source_songs = self.get_source_spotify_tracks(options)
        sample_data = self.get_sample_data(source_songs)


        spotify_dict = self.get_sample_spotify_tracks(sample_data)
        self.populate_output(options=options,
                             sample_tracks=spotify_dict)
        print(f'Created playlist {options.playlist_name}')
        return self.spot


    def from_search(self, search_term, content_type, direction=None, output_name=None, output_type=None):
        # FIXME: generalise search from get_sample_spotify_tracks
        options = Options()
        result = self.spot.search(search_term,
                                  limit=50)

        tree_obj = objectpath.Tree(result)
        search_mod = '.album' if content_type == options.ALBUM else ''
        query = f'$.tracks.items{search_mod}.(name, uri)'
        options.parent_name, reference = tuple(tree_obj.execute(query))[0] # get top result
        print()
        print(options.parent_name, reference)

        if self.debug: self.log(message='from_search',
                                content=('json', search_result))

        options.generate(
            reference=reference,
            direction=direction,
            content_type=options.CURRENT_SONG,
            output_name=output_name,
            output_type=output_type
        )

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
            results = self.spot.user_playlist(options.username, options.reference)
            track_parser = lambda track: track['track']

        if options.content_type == options.ALBUM:
            results = self.spot.album_tracks(options.reference)
            track_key = 'tracks'

        if options.content_type == options.SONG:
            results.append(self.spot.track(options.reference))

        if options.content_type == options.CURRENT_SONG:
            # FIXME: Spotipy API from package doesn't contain `current_song` function
            results.append(self.spot._get("me/player/currently-playing", market=None))

        return self.format_source_result(results, track_parser, options)

    def format_source_result(self, results, track_parser, options):
        og_tracks = []
        options.parent_name = results['name']
        for entry in results['tracks']['items']:
            track = track_parser(entry)
            artists = [prop['name'] for prop in track['artists']]
            og_tracks.append({
                'artist': artists,
                'track': track['name'].replace('Instrumental', '')
            })
        return og_tracks

    def get_sample_spotify_tracks(self, sample_tracks):
        """ Searches spotify for sample tracks """
        if self.debug: self.log('Checking Spotify for Samples')

        found_songs = []  # matches append {'detail': foo, 'search_query': baz, 'id': bar}
        unfound_list = [] # this is just a one-dimensional list
        for track in sample_tracks:
            sub_list = []
            title = track['title']
            artist = track['artist']
            null = lambda s, ss: s.replace(ss, ' ')
            s_artist = \
                null(null(null(null(null(artist.lower(), '&'), ' feat '), ' feat. '), ' the '), ' and ')
            detail = f'{track["query"]} -> {title}, by {artist}'
            search_query = f'{title} {s_artist}'
            result = self.spot.search(search_query,
                                      limit=10)['tracks']['items']
            for entry in result: # iter search results for first artist fuzzy match
                search_artist = entry['artists'][0]['name'].lower()
                if fuzz.token_set_ratio(search_artist, artist) > 90:
                    sub_list.append({
                        'detail': detail,
                        'search_query': search_query,
                        'id': entry['id']
                    })
                    break

            if sub_list: # hit
                found_songs.append(sub_list[0])
            else:        # no hit
                unfound_list.append({'detail': detail, 'search_query': search_query})


        find_rate = 1 - len(unfound_list) / len(sample_tracks)
        return {'found': found_songs, 'unfound': unfound_list, 'rate': find_rate}

    def get_sample_data(self, source_songs):
        new_playlist_tracks = self.scraper.get_whosampled_playlist(source_songs)
        return new_playlist_tracks


    def populate_output(self, options, sample_tracks):
        playlist_id = 0
        playlist_name = \
            options.output_name if options.output_name \
                                else f'SAMPLIFY: {options.parent_name}'
        options.playlist_name = playlist_name
        description = self.generate_description(
            sample_data=sample_tracks, options=options)
        if self.debug: print(description)

        if options.output_type == options.APPEND_ONLY or \
           options.output_type == options.APPEND_OR_CREATE:
            # search for user playlist where output_name == playlist name
            raise NotImplemented("Functionality not supported yet")

        if options.output_type == options.CREATE_ONLY and playlist_id == 0:
            # create playlist, then retrieve id

            playlist = self.spot.user_playlist_create(
                user=options.username, name=playlist_name,
                public=True) # FIXME: allow private playlists
            playlist_id = self.spot.user_playlists(options.username)['items'][0]['id']

        ids = [track['id'] for track in sample_tracks['found']]

        self.spot.user_playlist_add_tracks(
            options.username, playlist_id, ids, position=None)
        self.spot.user_playlist_change_details(
            playlist_id=playlist_id,description=description)

    def log(self, message, content):
        from time import time
        log_type, payload = content
        if log_type == 'json':
            payload = json.dumps(payload, indent=4)
        with open(f'{message}.{time()}.{log_type}', 'w+') as f:
            f.write(payload)

    def generate_description(self, sample_data, options):
        """
        Gives some information on the playlist.
        - Descriptions in spotify are 300 chars
        """
        print(sample_data)
        join = lambda key, sub_key: str.join('''
''', [track[sub_key] for track in sample_data[key]])
        unfound = join('unfound', 'detail')
        u_searches = join('unfound', 'search_query')
        found = join('found', 'detail')
        f_searches = join('found', 'search_query')
        rate = round(sample_data['rate'], 3)*100

        description = f'''
# {options.playlist_name}

This playlist was generated using Samplify.
Github: https://github.com/qzdl/samplify

The {options.content_type}, {options.parent_name}, has been broken down into:
"{options.direction.lower()}"

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
        print(description)
        return description


if __name__ == '__main__':
    options = Options()
    import argparse
    parser = argparse.ArgumentParser()
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument(
        '-l',
        '--link',
        help='Click "Share" > "Copy Link"'
    )
    reference_group.add_argument(
        '-s',
        '--search',
        help='Search as you would in the app'
    )

    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument(
        '--album',
        action="store_const",
        const=options.ALBUM,
        dest='content_type'
    )
    content_group.add_argument(
        '--playlist',
        action="store_const",
        const=options.PLAYLIST,
        dest='content_type'
    )
    content_group.add_argument(
        '--song',
        action="store_const",
        const=options.SONG,
        dest='content_type'
    )
    # FIXME: current song can't work with '--search'
    content_group.add_argument(
        '--current-song',
        action="store_const",
        const=options.CURRENT_SONG,
        dest='content_type'
    )

    parser.add_argument("--direction")
    parser.add_argument("--output-name")
    parser.add_argument("--output-type")
    parser.add_argument("--username")
    args = parser.parse_args()
    print('parsed args')
    print(args)

    default_options = Options()
    samplify = Samplify();
    result = None


    if args.search:
        result = samplify.from_search(
            search_term=args.search,
            direction=args.direction,
            content_type=args.content_type,
            output_name=args.output_name,
            output_type=args.output_type
        )


    if options.type_is_playlist(args.content_type):
        result = samplify.playlist(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )

    if options.type_is_album(args.content_type):
        result = samplify.album(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type
        )

    if options.type_is_song(args.content_type):
        result = samplify.song(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )

    if options.type_is_current_song(args.content_type):
        result = samplify.current_song(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )


    # Train of Thought, Reflection Eternal
    # s.album(reference='https://open.spotify.com/album/2PbWFmysd3j9MEacjjhozx?si=wbP_n3BZS8yqaSRM2opvVQ')
    # Daydream, Mariah Carey
    # s.album(reference='https://open.spotify.com/album/1ibYM4abQtSVQFQWvDSo4J?si=Gfgo2ZT5Sy2yYzLJZx2iGg)

#from sample_finder import Samplify;from tools import direction as d;s = Samplify();s.playlist('https://open.spotify.com/playlist/629QKIyhBqKaiPDWNHfw2z?si=QHtiuqNTRtWCGOAdRyiLhw', d.contains_sample_of)
