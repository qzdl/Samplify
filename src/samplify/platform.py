# -*- coding: utf-8 -*-
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import util

from samplify.config import config

SPOTIFY = 'spotify'
YOUTUBE = 'youtube'
STDOUT = 'stdout'

def get_platform(name):
    if name == SPOTIFY:
        return Spotify(0)
    if name == YOUTUBE:
        return Youtube(0)
    raise Exception(f'Invalid platform name: {name}')

class Platform:
    def __init__(self, verbosity=0):
        self.description = 'Generated with 💖 by Samplify. https://github.com/qzdl/samplify'

    def filter_nulls(self, tracks):
        """ For use with higher rate limits (i.e youtube)
        - (default) Behaviour is to just return whatever is passed in
        - Checks for invalid search candidates, reducing the set
          of tracks required to iterate.
        """
        return tracks

    def get_source_tracks(self, options):
        pass

    def search(self, query):
        pass

    def create_playlist(self, playlist_name, public=True, user=None,
                        short_description=None, long_description=None):
        pass

    def add_item_to_playlist(self, playlist_id, item_id):
        pass


class Spotify(Platform):
    def __init__(self, verbosity=0):
        self.name = SPOTIFY
        scope = 'playlist-modify-public'
        self.spotify = spotipy.Spotify(auth=self.get_token(scope))
        super().__init__(verbosity)


    def get_token(self, scope):
        token = util.prompt_for_user_token(
            config.username,
            scope,
            client_id=config.client,
            client_secret=config.secret,
            redirect_uri=config.redirect
        )
        return token


    def get_source_tracks(self, options):
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


    def search(self, query):
        """ Hits the search endpoint of the spotify API
        - term_builder is "first artist".lower()
        """
        term_builder = lambda entry: entry['artists'][0]['name'].lower()
        return term_builder, self.spotify.search(query, limit=10)['tracks']['items']


    def create_playlist(self, playlist_name, public=True, user=None,
                        short_description=None, long_description=None):
        short_description = self.description if not short_description else short_description
        long_description = self.description if not long_description else long_description

        self.spotify.user_playlist_create(
            user=user,
            name=playlist_name,
            public=True,
            description=short_description
        )

        # return playlist_id (gets most recent playlist)
        return self.spotify.user_playlists(user)['items'][0]['id']


    def add_items_to_playlist(self, playlist_id, track_ids, user, origin_name=None):
        self.spotify.user_playlist_add_tracks(
            user, playlist_id, track_ids, position=None)


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


class Youtube(Platform):
    def __init__(self, verbosity):
        """ Youtube intialisation
        - define scopes
        - load config
        - oauth2 flow
        - generate session context
        """
        self.name = YOUTUBE
        self.music_category_id = 10
        # call parent ctor
        super().__init__(verbosity)

        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "config/client.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        self.yt_session = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)


    def get_source_tracks(self, options):
        pass


    def search(self, query):
        """ Hits the search endpoint
        - Restricts by categoryId = music (10)
        - term_builder = query
        """
        search_response = self.yt_session.search().list(
            q=query,
            part="id,snippet",
            maxResults=10,
            type='video' # FIXME: restrict to videos
        ).execute()

        # FIXME: I'm sure there's something better we can do here
        #        for now, just use the OG search term
        term_builder = lambda entry: query

        for entry in search_response:
            print()
            print(f'entry found for {query}')
            print(f'title: {search_result["snippet"]["title"]}')

        # TODO: shape this up
        return term_builder, [entry for entry in search_response]


    def create_playlist(self, playlist_name, public=True, user=None,
                        short_description=None, long_description=None):
        short_description = self.description if not short_description else short_description
        long_description = self.description if not long_description else long_description

        self.yt_session.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": playlist_name,
                    "description": description,
                    "tags": [
                        "SAMPLIFY",
                        "samplify",
                        "hiphopheads",
                        "QZDL",
                        "VinRican"
                    ],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": "private"
                }
            }
        ) # end insert
        return request.execute()


    def add_items_to_playlist(self, playlist_id, track_ids, origin_name=None):
        # TODO: check responses for failures
        # TODO: check for existing VinRican video on the album
        if origin_name:
            rican = self.search(query=f'discover samples in ')
        if rican:
            track_ids.append(rican) # TODO: extract id
        responses = []
        for id in track_ids:
            responses.append(self.add_item_to_playlist(playlist_id, item_id))


    def add_item_to_playlist(self, playlist_id, item_id):
        add_request=self.yt_session.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            })  # end insert
        return add_request.execute() # yields body of request


class StdOut(Platform):
    pass
