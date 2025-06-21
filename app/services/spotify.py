import spotipy
from flask import current_app
from spotipy import SpotifyOAuth


class SpotipyClient:
    """
    A singleton client for interacting with the Spotify Web API.
    
    This class provides a centralized interface for all Spotify API operations,
    implementing the singleton pattern to ensure only one instance exists
    throughout the application lifecycle.
    """
    
    _instance = None

    def __new__(cls, client_id=None, client_secret=None, redirect_uri=None):
        """
        Create or return the singleton instance of SpotipyClient.
        
        Args:
            client_id (str, optional): Spotify client ID
            client_secret (str, optional): Spotify client secret
            redirect_uri (str, optional): Spotify redirect URI
            
        Returns:
            SpotipyClient: The singleton instance of the client
        """
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
        """
        Retrieve the user's recently played tracks from Spotify.
        
        Args:
            limit (int): Maximum number of tracks to retrieve (1-50)
            
        Returns:
            dict: Spotify API response containing recently played tracks
            
        Status codes:
            - 200: Successfully retrieved tracks
            - 401: Authentication error
            - 400: Invalid request parameters
        """
        return self.sp.current_user_recently_played(limit=limit)

    def get_currently_playing_track(self):
        """
        Get information about the track currently playing on the user's Spotify account.
        
        Returns:
            dict or None: Spotify API response containing current track information
                or None if no track is currently playing
            
        Status codes:
            - 200: Successfully retrieved current track
            - 204: No track is currently playing
            - 401: Authentication error
        """
        return self.sp.current_user_playing_track()

    def get_top_artists(self, limit):
        """
        Retrieve the user's top artists based on listening history.
        
        Args:
            limit (int): Maximum number of artists to retrieve (1-50)
            
        Returns:
            dict: Spotify API response containing top artists information
            
        Status codes:
            - 200: Successfully retrieved top artists
            - 401: Authentication error
            - 400: Invalid request parameters
        """
        return self.sp.current_user_top_artists(limit)

    def get_saved_albums(self, limit):
        """
        Retrieve albums that the user has saved to their Spotify library.
        
        Args:
            limit (int): Maximum number of albums to retrieve (1-50)
            
        Returns:
            dict: Spotify API response containing saved albums information
            
        Status codes:
            - 200: Successfully retrieved saved albums
            - 401: Authentication error
            - 400: Invalid request parameters
        """
        return self.sp.current_user_saved_albums(limit)
    
    def search_albums(self, auth, query, limit):
        """
        Search for albums on Spotify using a query string.
        
        Args:
            auth (str): Spotify access token for authentication
            query (str): Search query string to find albums
            limit (int): Maximum number of search results to return (1-50)
            
        Returns:
            list: List of dictionaries containing formatted album information:
                - name (str): Album name
                - id (str): Spotify album ID
                - artist (str): Primary artist name
                - release_date (str): Album release date
                - total_tracks (int): Number of tracks on the album
                - image (str or None): Album cover image URL
                - album_type (str): Type of album
            
        Status codes:
            - 200: Successfully performed search
            - 401: Authentication error
            - 400: Missing query parameter
        """
        self.sp.auth = auth
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

    def search_artists_albums(self, auth, query, limit):
        """
        Search for both artists and albums on Spotify using a query string.
        
        Args:
            auth (str): Spotify access token for authentication
            query (str): Search query string to find artists and albums
            limit (int): Maximum number of search results to return (1-50)
            
        Returns:
            dict: Dictionary containing two lists - 'artists' and 'albums':
                
                artists (list): List of artist dictionaries:
                    - name (str): Artist name
                    - id (str): Spotify artist ID
                    - image (str or None): Artist profile image URL
                
                albums (list): List of album dictionaries:
                    - name (str): Album name
                    - id (str): Spotify album ID
                    - artist (str): Primary artist name
                    - release_date (str): Album release date
                    - total_tracks (int): Number of tracks
                    - image (str or None): Album cover image URL
                    - album_type (str): Type of album
            
        Status codes:
            - 200: Successfully performed search
            - 401: Authentication error
            - 400: Missing query parameter
        """
        self.sp.auth = auth
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
        
    def get_user(self, auth, spotify_id):
        """
        Retrieve information about a Spotify user by their Spotify ID.
        
        Args:
            auth (str): Spotify access token for authentication
            spotify_id (str): The Spotify user ID of the user to retrieve
            
        Returns:
            dict: Dictionary containing formatted user information:
                - user (dict): User details:
                    - display_name (str): User's display name
                    - id (str): Spotify user ID
                    - image (str or None): User's profile image URL
            
        Status codes:
            - 200: Successfully retrieved user information
            - 401: Authentication error
            - 404: User not found
        """
        self.sp.auth = auth
        user = self.sp.user(spotify_id)
        return {
            "user": {
                    "display_name": user["display_name"],
                    "id": user["id"],
                    "image": user["images"][0]["url"] if user["images"] else None,
                } 
         }

