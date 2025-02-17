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
    
    def search_albums(self,auth, query, limit):
        self.sp.auth= auth
        results = self.sp.search(q=query, limit=limit, type='album')
        albums = results.get('albums', {}).get('items', [])

        return [
            {
                "name": album["name"],
                "id": album["id"],
                "artist": album["artists"][0]["name"] if album["artists"] else "Unknown",
                "release_date": album["release_date"],
                "total_tracks": album["total_tracks"],
                "image": album["images"][0]["url"] if album["images"] else None,
                "album_type": album["album_type"]
            }
            for album in albums
        ]

    def search_artists_albums(self,auth, query, limit):
        self.sp.auth=auth
        results = self.sp.search(q=query, limit=limit, type='artist,album')
        artists = results.get('artists', {}).get('items', [])
        albums = results.get('albums', {}).get('items', [])

        return {
            "artists": [
                {
                    "name": artist["name"],
                    "id": artist["id"],
                    "image": artist["images"][0]["url"] if artist["images"] else None
                } for artist in artists
            ],
            "albums": [
                {
                    "name": album["name"],
                    "id": album["id"],
                    "artist": album["artists"][0]["name"] if album["artists"] else "Unknown",
                    "release_date": album["release_date"],
                    "total_tracks": album["total_tracks"],
                    "image": album["images"][0]["url"] if album["images"] else None,
                    "album_type": album["album_type"]
                } for album in albums
            ]
        }
