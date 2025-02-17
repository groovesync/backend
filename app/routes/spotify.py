from flask import Blueprint, request, jsonify
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
        data = spotipy_client.search_artists_albums(spotify_access_token, query, limit)
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
    
    try:
        albums = spotipy_client.search_albums(spotify_access_token, query, limit)
        return jsonify({"success": True, "data": albums}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
