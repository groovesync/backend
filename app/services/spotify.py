import spotipy
from flask import current_app
from spotipy import SpotifyOAuth


class SpotipyClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpotipyClient, cls).__new__(cls)
            cls._instance.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'],
                scope='user-read-recently-played user-read-currently-playing user-top-read',
            ))
        return cls._instance

    def get_recent_tracks(self, limit):
        return self.sp.current_user_recently_played(limit=limit)

    def get_currently_playing_track(self):
        return self.sp.current_user_playing_track()

    def get_top_artists(self, limit):
        return self.sp.current_user_top_artists(limit)
