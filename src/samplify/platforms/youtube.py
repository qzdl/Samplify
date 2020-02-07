# -*- coding: utf-8 -*-

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

"""
A set of mappings is required for youtube to create playlists
- Is there a youtube python client?
- What sort of auth is required?
- Docs require update
- sample_finder.py needs to be further refactored to remove common elements
  like mapping & interpretation of whosampled results.
"""

class Youtube:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = "client.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        self.yt_session = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def create_playlist(self, playlist_name, description):
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


    def add_video_to_playlist(self, video_id, playlist_id):
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
