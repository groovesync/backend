import spotipy
from flask import current_app
from spotipy import SpotifyOAuth


class SpotipyClient:
    _instance = None

    def __new__(cls, client_id=None, client_secret=None, redirect_uri=None):
        if cls._instance is None:
            cls._instance = super(SpotipyClient, cls).__new__(cls)

            client_id = client_id or current_app.config.get('SPOTIFY_CLIENT_ID')
            client_secret = client_secret or current_app.config.get('SPOTIFY_CLIENT_SECRET')
            redirect_uri = redirect_uri or current_app.config.get('SPOTIFY_REDIRECT_URI')

            cls._instance.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope='user-read-recently-played user-read-currently-playing user-top-read user-library-read',
            ))

        return cls._instance

    def get_recent_tracks(self, limit):
        return self.sp.current_user_recently_played(limit=limit)

    def get_currently_playing_track(self):
        return self.sp.current_user_playing_track()

    def get_top_artists(self, limit):
        return self.sp.current_user_top_artists(limit)

    def get_saved_albums(self, limit):
        return self.sp.current_user_saved_albums(limit)