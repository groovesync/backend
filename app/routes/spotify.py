from flask import Blueprint, request, jsonify
from app.routes.user import token_required
from app.services.spotify import SpotipyClient

bp = Blueprint('spotify', __name__, url_prefix='/spotify')

@bp.route('/recent-tracks', methods=['GET'])
@token_required
def get_recent_tracks():
    tracks = SpotipyClient().get_recent_tracks(5)
    return jsonify({"success": True, "data": tracks}), 200


@bp.route('/current-track', methods=['GET'])
@token_required
def get_current_track():
    track = SpotipyClient().get_currently_playing_track()
    if track is not None:
        return jsonify({"success": True, "data": track}), 200
    else:
        return jsonify({"success": False, "message": "No track is currently playing"}), 204


@bp.route('/obsessions', methods=['GET'])
@token_required
def get_top_items():
    limit = request.args.get('limit', default=5, type=int)
    top_items = SpotipyClient().get_top_artists(limit)
    return jsonify({"success": True, "data": top_items}), 200

