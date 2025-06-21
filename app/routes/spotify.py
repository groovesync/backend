from flask import Blueprint, request, jsonify

from app.models.review import Review
from app.models.user import User
from app.models.favorite import Favorite
from app.routes.user import token_required
import spotipy
import random

bp = Blueprint('spotify', __name__, url_prefix='/spotify')
RELEASE_OFFSET = random.randint(10, 30)

@bp.route('/recent-tracks', methods=['GET'])
@token_required
def get_recent_tracks():
    """
    Get the user's recently played tracks from Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing recent tracks
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved recent tracks
        - 401: Missing or invalid Spotify access token
        - 400: Error fetching recent tracks from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        tracks = sp.current_user_recently_played(limit=5)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching recent tracks", "error": str(e)}), 400

    return jsonify({"success": True, "data": tracks}), 200


@bp.route('/current-track', methods=['GET'])
@token_required
def get_current_track():
    """
    Get the currently playing track for the authenticated user.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing current track info
            - message (str): Error message if operation fails or no track playing
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved current track
        - 204: No track is currently playing
        - 401: Missing or invalid Spotify access token
        - 400: Error fetching current track from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        track = sp.current_user_playing_track()
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching currently playing", "error": str(e)}), 400

    if track is not None:
        return jsonify({"success": True, "data": track}), 200
    else:
        return jsonify({"success": False, "message": "No track is currently playing"}), 204


@bp.route('/obsessions', methods=['GET'])
@token_required
def get_top_items():
    """
    Get the user's top artists (obsessions) from Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing top artists
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved top artists
        - 401: Missing or invalid Spotify access token
        - 400: Error fetching top artists from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        top_items = sp.current_user_top_artists(
            limit=5, offset=0, time_range='short_term')
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching user obsessions", "error": str(e)}), 400
    return jsonify({"success": True, "data": top_items}), 200


@bp.route('/artist/<artist_id>', methods=['GET'])
@token_required
def get_artist(artist_id):
    """
    Get detailed information about a specific artist.
    
    Args:
        artist_id (str): Spotify artist ID
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing artist information
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved artist information
        - 401: Missing or invalid Spotify access token
        - 400: Error fetching artist data from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        artist = sp.artist(artist_id)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching artist data", "error": str(e)}), 400
    return jsonify({"success": True, "data": artist}), 200


@bp.route('/artist/<artist_id>/albums', methods=['GET'])
@token_required
def get_album_by_artist(artist_id):
    """
    Get all albums by a specific artist.
    
    Args:
        artist_id (str): Spotify artist ID
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing artist's albums
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved artist albums
        - 401: Missing or invalid Spotify access token
        - 400: Error fetching artist albums from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        albums = sp.artist_albums(artist_id, "album")
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching artist data", "error": str(e)}), 400
    return jsonify({"success": True, "data": albums}), 200


@bp.route('/saved-albums', methods=['GET'])
@token_required
def get_saved_albums():
    """
    Get the user's saved albums from Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing saved albums
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved saved albums
        - 401: Missing or invalid Spotify access token
        - 500: Error fetching saved albums from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        saved_albums = sp.current_user_saved_albums()
        return jsonify({"success": True, "data": saved_albums}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching saved albums", "error": str(e)}), 500

@bp.route('/recommendations', methods=['GET'])
@token_required
def get_recommendation():
    """
    Get new release recommendations for the user.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing new releases
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved recommendations
        - 401: Missing or invalid Spotify access token
        - 500: Error fetching recommendations from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        recommendations = sp.new_releases(limit=10, offset=RELEASE_OFFSET)
        return jsonify({"success": True, "data": recommendations}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching recommendations", "error": str(e)}), 500

@bp.route('/new-releases', methods=['GET'])
@token_required
def get_new_releases():
    """
    Get the latest new releases from Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing new releases
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved new releases
        - 401: Missing or invalid Spotify access token
        - 500: Error fetching new releases from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        new_releases = sp.new_releases(limit=6, offset=(RELEASE_OFFSET+10+random.randint(3,6)))
        return jsonify({"success": True, "data": new_releases}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching new releases", "error": str(e)}), 500


@bp.route('/search', methods=['GET'])
@token_required
def search_artists_and_albums():
    """
    Search for artists and albums on Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Query Parameters:
        q (str): Search query string (required)
        limit (int): Maximum number of results to return (default: 20)
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - artists (dict): Spotify API response containing artist search results
            - albums (dict): Spotify API response containing album search results
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully performed search
        - 400: Missing query parameter or search error
        - 401: Missing or invalid Spotify access token
        - 500: Error performing search on Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=20, type=int)

    if not query:
        return jsonify({"success": False, "message": "Query parameter 'q' is required"}), 400

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        data = sp.search(q=query, type='artist,album', limit=limit)
        if data is None:
            return jsonify({"success": False, "message": "No search results found"}), 404
        return jsonify({"success": True, "artists": data["artists"], "albums": data["albums"]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/search/albums', methods=['GET'])
@token_required
def search_albums():    
    """
    Search for albums only on Spotify.
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Query Parameters:
        q (str): Search query string (required)
        limit (int): Maximum number of results to return (default: 10)
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing album search results
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully performed album search
        - 400: Missing query parameter
        - 401: Missing or invalid Spotify access token
        - 500: Error performing search on Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)

    if not query:
        return jsonify({"success": False, "message": "Query parameter 'q' is required"}), 400    
    
    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        albums = sp.search(q=query, type='album', limit=limit)
        return jsonify({"success": True, "data": albums}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/users/<spotify_id>', methods=['GET'])
@token_required
def get_user(spotify_id):
    """
    Get information about a Spotify user by their Spotify ID.
    
    Args:
        spotify_id (str): Spotify user ID
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - data (dict): Spotify API response containing user information
            - message (str): Error message if operation fails
            - error (str): Detailed error information if applicable
    
    Status codes:
        - 200: Successfully retrieved user information
        - 401: Missing or invalid Spotify access token
        - 500: Error fetching user data from Spotify API
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        user = sp.user(spotify_id)
        return jsonify({"success": True, "data": user}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/albums/<album_id>', methods=['GET'])
@token_required
def get_album_details(album_id):
    """
    Get detailed information about a specific album including reviews and user interactions.
    
    Args:
        album_id (str): Spotify album ID
    
    Headers:
        Spotify-Token (str): Valid Spotify access token
        Authorization (str): Bearer token for user authentication
    
    Query Parameters:
        user_id (str): User ID for retrieving personal reviews and favorites (required)
    
    Returns:
        JSON response with:
            - success (bool): True if operation successful
            - album_info (dict): Complete album information including:
                - name (str): Album name
                - id (str): Spotify album ID
                - image (str): Album cover image URL
                - url (str): Spotify album URL
                - artists (list): List of artist objects with name and ID
                - release_year (str): Year of release
                - overall_rating (float): Average rating from all reviews
                - your_rating (float): User's personal rating (if exists)
                - your_review (str): User's review text (if exists)
                - your_review_id (str): User's review ID (if exists)
                - reviews (list): Other users' reviews with profile info
                - is_favorite (bool): Whether user has favorited this album
                - favorite_id (str): Favorite record ID (if favorited)
            - message (str): Error message if operation fails
    
    Status codes:
        - 200: Successfully retrieved album details
        - 204: No album found
        - 400: Missing user_id parameter or error fetching album
        - 401: Missing or invalid Spotify access token
    """
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)

    user_id = request.args.get("user_id", default="", type=str)
    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    try:
        album = sp.album(album_id)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching album", "error": str(e)}), 400

    if album is None:
        return jsonify({"success": False, "message": "No album found"}), 204

    album_name = album['name']
    album_url = album['external_urls']['spotify']
    artists = [{"name": artist['name'], "id": artist["id"]} for artist in album['artists']]
    release_year = album['release_date'][:4]

    is_favorite_of_user = Favorite.is_favorite(user_id, album_id)
    favorite_id = Favorite.get_favorite_id(user_id, album_id)

    reviews = Review.get_by_album(album_id)
    if not reviews:
        return jsonify({
            "success": True,
            "message": "No reviews yet",
            "album_info": {
                "name": album_name,
                "id": album["id"],
                "image": album["images"][0]["url"],
                "url": album_url,
                "artists": artists,
                "release_year": release_year,
                "overall_rating": None,
                "your_rating": None,
                "reviews": [],
                "your_review": None,
                "is_favorite": is_favorite_of_user,
                "favorite_id": favorite_id
            }
        }), 200

    overall_rating = round(sum(review['rate'] for review in reviews) / len(reviews), 1)

    user_review = next((review for review in reviews if review['userId'] == user_id), None)
    your_rating = user_review['rate'] if user_review else None
    your_review = user_review['text'] if user_review else None
    your_review_id = user_review["_id"] if user_review else None

    other_reviews = []
    for review in reviews:
        if review['userId'] != user_id:
            user = User.find_user_by_spotify_id(review['userId'])
            if user:
                spotify_id = user['spotify_id']
                try:
                    user_details = sp.user(spotify_id)
                    if user_details and user_details.get('images'):
                        other_reviews.append({
                            "username": user_details['display_name'],
                            "profile_picture": user_details['images'][0]['url'],
                            "rate": review['rate'],
                            "text": review['text'],
                            "user_id": user["spotify_id"]
                        })
                    elif user_details:
                        other_reviews.append({
                            "username": user_details.get('display_name', 'Unknown User'),
                            "profile_picture": None,
                            "rate": review['rate'],
                            "text": review['text'],
                            "user_id": user["spotify_id"]
                        })
                    else:
                        other_reviews.append({
                            "username": "Unknown User",
                            "profile_picture": None,
                            "rate": review['rate'],
                            "text": review['text'],
                            "user_id": user["spotify_id"]
                        })
                except Exception:
                    # Fallback if Spotify user details can't be fetched
                    other_reviews.append({
                        "username": "Unknown User",
                        "profile_picture": None,
                        "rate": review['rate'],
                        "text": review['text'],
                        "user_id": user["spotify_id"]
                    })

    return jsonify({
        "success": True,
        "album_info": {
            "name": album_name,
            "url": album_url,
            "image": album["images"][0]["url"],
            "artists": artists,
            "release_year": release_year,
            "overall_rating": overall_rating,
            "your_rating": your_rating,
            "your_review": your_review,
            "your_review_id": your_review_id,
            "reviews": other_reviews,
            "is_favorite": is_favorite_of_user,
            "favorite_id": favorite_id,
            "id": album["id"]
        }
    }), 200

