from flask import Blueprint, request, jsonify

from app.models.review import Review
from app.models.user import User
from app.models.favorite import Favorite
from app.routes.user import token_required
import spotipy

bp = Blueprint('spotify', __name__, url_prefix='/spotify')

@bp.route('/recent-tracks', methods=['GET'])
@token_required
def get_recent_tracks():
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
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        saved_albums = sp.current_user_saved_albums()
        return jsonify({"success": True, "data": saved_albums}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error fetching saved albums", "error": str(e)}), 500


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

    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        data = sp.search(q=query, type='artist,album', limit=limit)
        return jsonify({"success": True, "artists": data["artists"], "albums": data["albums"]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


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
    
    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        albums = sp.search(q=query, type='album', limit=limit)
        return jsonify({"success": True, "data": albums}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/users/<spotify_id>', methods=['GET'])
@token_required
def get_user(spotify_id):
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
            "image": album["images"][0]["url"],
            "artists": artists,
            "release_year": release_year,
            "overall_rating": overall_rating,
            "your_rating": your_rating,
            "your_review": your_review,
            "reviews": other_reviews,
            "is_favorite": is_favorite_of_user,
            "favorite_id": favorite_id,
            "id": album["id"]
        }
    }), 200

