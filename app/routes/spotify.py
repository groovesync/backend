from flask import Blueprint, request, jsonify
from app.routes.user import token_required
from app.services.spotify import SpotipyClient

bp = Blueprint('spotify', __name__, url_prefix='/spotify')
spotipy_client = SpotipyClient()  


@bp.route('/recent-tracks', methods=['GET'])
@token_required
def get_recent_tracks():
    tracks = spotipy_client.get_recent_tracks(5)
    return jsonify({"success": True, "data": tracks}), 200


@bp.route('/current-track', methods=['GET'])
@token_required
def get_current_track():
    track = spotipy_client.get_currently_playing_track()
    if track is not None:
        return jsonify({"success": True, "data": track}), 200
    else:
        return jsonify({"success": False, "message": "No track is currently playing"}), 204


@bp.route('/obsessions', methods=['GET'])
@token_required
def get_top_items():
    limit = request.args.get('limit', default=5, type=int)
    top_items = spotipy_client.get_top_artists(limit)
    return jsonify({"success": True, "data": top_items}), 200

@bp.route('/saved-albums', methods=['GET'])
@token_required
def get_saved_albums():
    limit = request.args.get('limit', default=5, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    try:
        albums = spotipy_client.get_saved_albums(limit, offset)
        return jsonify({"success": True, "data": albums}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

