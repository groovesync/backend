from flask import Blueprint, request, jsonify
from app.models.follow import Follow
import spotipy

bp = Blueprint('follow', __name__, url_prefix='/follow')

@bp.route('/add', methods=["POST"])
def follow_user():
    data = request.get_json()
    try:
        follow = Follow(
            spotify_id_1=data["spotifyId1"],
            spotify_id_2=data["spotifyId2"]
        )
        follow_id = follow.save()
        return jsonify({"success": True, "follow_id": str(follow_id)}), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@bp.route('/remove', methods=["DELETE"])
def unfollow_user():
    spotify_id_1 = request.args.get('spotifyId1', default="", type=str)
    spotify_id_2 = request.args.get('spotifyId2', default="", type=str)
    try:
        success = Follow.delete(spotify_id_1, spotify_id_2)
        if success:
            return jsonify({"success": True}), 201
        return jsonify({"success": False}), 204
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@bp.route('/following/<spotify_id>', methods=['GET'])
def get_following(spotify_id):
    following = Follow.get_following(spotify_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    if following:
        enriched_following = []
        for follow in following:
            spotifyId = follow["spotifyId2"]
            sp = spotipy.Spotify(auth=spotify_access_token)
            try:
                user = sp.user(spotifyId)
                enriched_following.append({
                    "user_id": spotifyId,
                    "user_display_name": user["display_name"],
                    "user_image": user["images"][0]["url"]
                })
                return jsonify({"following": enriched_following}), 200
            except Exception as e:
                return jsonify({"success": False, "message": "Error fetching user information", "error": str(e)}), 400
        return jsonify({"following": enriched_following}), 200
    return jsonify({"following": None}), 200

@bp.route('/followers/<spotify_id>', methods=['GET'])
def get_followers(spotify_id):
    followers = Follow.get_followers(spotify_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    if followers:
        enriched_followers = []
        for follow in followers:
            spotifyId = follow["spotifyId1"]
            sp = spotipy.Spotify(auth=spotify_access_token)
            try:
                user = sp.user(spotifyId)
                enriched_followers.append({
                    "user_id": spotifyId,
                    "user_display_name": user["display_name"],
                    "user_image": user["images"][0]["url"]
                })
                return jsonify({"followers": enriched_followers}), 200
            except Exception as e:
                return jsonify({"success": False, "message": "Error fetching user information", "error": str(e)}), 400
        return jsonify({"followers": followers}), 200
    return jsonify({"followers": None}), 200

