import json
from time import time
from spotipy import util
from fuzzywuzzy import fuzz
import objectpath

from tools.whosampled import Scraper
from tools.options import Options
from tools.logger import Logger
from tools import direction as d

from platforms import platform
from config import config as cfg

# uri => spotify:album:2laBNOqPW85M3js7qCYhKt
# http => https://open.spotify.com/album/2laBNOqPW85M3js7qCYhKt?si=QkZUkYZpSpuT1Xir6z7hGw

class Samplify(object):
    def __init__(self, input_platform, output_platform, verbosity=0):
        self.verbosity = verbosity
        self.logger = Logger(verbosity=self.verbosity, log_file=f'Samplify-{time()}')
        self.scraper = Scraper(verbosity=self.verbosity)
        self.input_platform = platform.get_platform(input_platform)
        self.output_platform = platform.get_platform(output_platform) \
            if input_platform != output_platform \
            else input_platform

    def samplify(self, options):
        """ The most general endpoint for interacting with samplify

        """
        source_songs = self.input_platform.get_source_tracks(options)
        sample_data = self.scraper.get_whosampled_playlist(source_songs, options.direction)

        sample_dict = self.get_sample_matches_from_platform(sample_data, options)
        options.output_name, description = self.populate_output(
            options=options,
            sample_tracks=sample_dict
        )

        self.log(message=f'\n{description}')
        self.log(message=f'Created playlist {options.playlist_name}')
        return description, self.input_platform, self.output_platform

    def from_search(self, search_term, content_type,
                    direction=None, output_name=None, output_type=None):
        options = Options()
        result = self.input_platform.search(search_term)
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


    def get_sample_tracks(self, sample_tracks, options):
        """ Searches output_platform for sample tracks
        if options.include_originator, the originator is placed in found_songs
        """
        found_songs = []  # matches append {'detail': foo, 'search_query': baz, 'id': bar}
        unfound_list = [] # this is just a one-dimensional list
        self.log(
            message=f'Checking {self.platform.name} for Samples',
            function='get_sample_tracks',
            data=sample_tracks
        )

        total_sample_count = 0
        # iter the originators (fixed as input size)
        for source_track in sample_tracks:
            og_title = source_track['track']
            originator_used = False
            use_originator = lambda s: found_songs.append({
                'detail': 'The originator of sample data',
                'search_query': 'n/a',
                'id': s['uri']
            });

            # direction is obj as -> { 'Was sampled in ': [{}, ...] }
            # iter directions for each track (1:n)
            for direction, tracks in source_track['samples'].items():
                total_sample_count = total_sample_count + len(tracks)
                found_unfound = self.get_sample_matches_from_platform(tracks, og_title, direction)

                if not originator_used \
                   and direction == d.was_sampled_in:
                    originator_used = True
                    use_originator(source_track)

                found_songs = found_songs + found_unfound[0]
                unfound_list = unfound_list + found_unfound[1]

                if not originator_used:
                    originator_used = True
                    use_originator(source_track)

        find_rate = 1 - len(unfound_list) / total_sample_count
        return {'found': found_songs, 'unfound': unfound_list, 'rate': find_rate}

    def get_sample_matches_from_platform(self, tracks, og_title, direction):
        """ Get the IDs required to create a playlist on the output platform

        """
        found_list = []
        unfound_list = []

        tracks = self.platform.filter_nulls(tracks)
        # iter each sample in the given direction
        for track in tracks:
            sub_list = []
            title = track['title']
            artist = track['artist'][0]
            detail = f'( {og_title} )->-[ {direction} ]->-( {title}, by {artist} )'
            search_query = f'{title} {artist}'

            self.log(message=f'Searching {self.output_platform.name} with {search_query}',
                    function='get_sample_matches_from_platform',
                    data=f'query: {search_query}\ndetail:{detail}')

            term_builder, result = self.output_platform.search(search_query)
            # iter search results for first artist fuzzy match
            for entry in result: # it's worth noting that we're 4 levels of `for` loops deep here lmao
                term = term_builder(entry)
                if fuzz.token_set_ratio(term, artist) < 90:
                    self.log(message=f'no match for s:{search_query}, r:{entry["name"]}',
                             function='get_matches_from_platform')
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


    def populate_output(self, options, sample_tracks):
        playlist_name = f'SAMPLIFY: {options.output_name}' \
            if options.output_name \
            else f'SAMPLIFY: {options.parent_name}'

        options.playlist_name = playlist_name
        short_description, long_description = self.generate_description(
            sample_data=sample_tracks, options=options)

        if options.output_type == options.CREATE_ONLY and playlist_id == 0:
            # create playlist, then retrieve id
            playlist_id = self.output_platform.create_playlist(
                playlist_name=playlist_name,
                long_description=long_description,
                short_description=short_description,
                public=True,
                user=options.username
            )

        track_ids = [track['id'] for track in sample_tracks['found']]
        self.output_platform.add_items_to_playlist(
            playlist_id,
            track_ids,
            origin_name=options.parent_name
        )

        return playlist_name, f'{short_description}\n{long_description}'

    def generate_description(self, sample_data, options):
        """
        Gives some information on the playlist.
        - Note that descriptions in spotify are 300 chars
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
