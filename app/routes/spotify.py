from flask import Blueprint, request, jsonify

from app.models.review import Review
from app.models.user import User
from app.routes.user import token_required
from app.services.spotify import SpotipyClient
import spotipy

bp = Blueprint('spotify', __name__, url_prefix='/spotify')
spotipy_client = SpotipyClient()


@bp.route('/recent-tracks', methods=['GET'])
@token_required
def get_recent_tracks():
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        tracks = spotipy_client.get_recent_tracks(spotify_access_token)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching recent tracks", "error": str(e)}), 400

    return jsonify({"success": True, "data": tracks}), 200


@bp.route('/current-track', methods=['GET'])
@token_required
def get_current_track():
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        track = spotipy_client.get_currently_playing_track(spotify_access_token)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching currently playing", "error": str(e)}), 400

    if track is not None:
        return jsonify({"success": True, "data": track}), 200
    else:
        return jsonify({"success": False, "message": "No track is currently playing"}), 204


@bp.route('/obsessions', methods=['GET'])
@token_required
def get_top_items():
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        top_items = spotipy_client.get_top_artists(spotify_access_token)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching user obsessions", "error": str(e)}), 400
    return jsonify({"success": True, "data": top_items}), 200


@bp.route('/artist/<artist_id>', methods=['GET'])
@token_required
def get_artist(artist_id):
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        artist = spotipy_client.get_artist(spotify_access_token, artist_id)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching artist data", "error": str(e)}), 400
    return jsonify({"success": True, "data": artist}), 200


@bp.route('/artist/<artist_id>/albums', methods=['GET'])
@token_required
def get_album_by_artist(artist_id):
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        albums = spotipy_client.get_artist_albuns(spotify_access_token, artist_id)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching artist data", "error": str(e)}), 400
    return jsonify({"success": True, "data": albums}), 200


@bp.route('/saved-albums', methods=['GET'])
@token_required
def get_saved_albums():
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        saved_albums = spotipy_client.get_saved_albums(spotify_access_token)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching saved albums", "error": str(e)}), 500
<<<<<<< HEAD
    return jsonify({"success": True, "data": saved_albums}), 200

    
=======


>>>>>>> e8882ca (Issue #19)
@bp.route('/search', methods=['GET'])
@token_required
def search_artists_and_albums():
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=20, type=int)

    if not query:
        return jsonify({"success": False, "message": "Query parameter 'q' is required"}), 400

    try:
        data = spotipy_client.search_artists_albums(spotify_access_token, query, limit)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching search data", "error": str(e)}), 500
    return jsonify({"success": True, "artists": data["artists"], "albums": data["albums"]}), 200



@bp.route('/search/albums', methods=['GET'])
@token_required
def search_albums():    
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)

    if not query:
        return jsonify({"success": False, "message": "Query parameter 'q' is required"}), 400    
    
    try:
        albums = spotipy_client.search_albums(spotify_access_token, query, limit)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching search data", "error": str(e)}), 500
    return jsonify({"success": True, "data": albums}), 200



@bp.route('/users/<spotify_id>', methods=['GET'])
@token_required
def get_user(spotify_id):
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    try:
        user = spotipy_client.get_user(spotify_access_token, spotify_id)
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching user data",  "error": str(e)}), 500
    return jsonify({"success": True, "data": user}), 200
    

@bp.route('/albums/<album_id>', methods=['GET'])
@token_required
def get_album_details(album_id):
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)

    data = request.get_json()
    user_id = data.get('user_id')
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
    artists = [artist['name'] for artist in album['artists']]
    release_year = album['release_date'][:4]

    reviews = Review.get_by_album(album_id)
    if not reviews:
        return jsonify({
            "success": True,
            "message": "No reviews yet",
            "album_info": {
                "name": album_name,
                "url": album_url,
                "artists": artists,
                "release_year": release_year,
                "overall_rating": None,
                "your_rating": None,
                "reviews": [],
                "your_review": None
            }
        }), 200

    overall_rating = round(sum(review['rate'] for review in reviews) / len(reviews), 1)

    user_review = next((review for review in reviews if review['userId'] == user_id), None)
    your_rating = user_review['rate'] if user_review else None
    your_review = user_review['text'] if user_review else None

    other_reviews = []
    for review in reviews:
        if review['userId'] != user_id:
            user = User.find_user_by_id(review['userId'])
            if user:
                spotify_id = user['spotify_id']
                user_details = sp.user(spotify_id)
                other_reviews.append({
                    "username": user_details['display_name'],
                    "profile_picture": user_details['images'][0]['url'] if user_details['images'] else None,
                    "rate": review['rate'],
                    "text": review['text']
                })

    return jsonify({
        "success": True,
        "album_info": {
            "name": album_name,
            "url": album_url,
            "artists": artists,
            "release_year": release_year,
            "overall_rating": overall_rating,
            "your_rating": your_rating,
            "your_review": your_review,
            "reviews": other_reviews
        }
    }), 200

