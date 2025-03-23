from flask import Blueprint, request, jsonify
from app.models.user import User
import spotipy

bp = Blueprint('follow', __name__, url_prefix='/follow')

@bp.route('/add', methods=['POST'])
def follow_user():
    data = request.get_json()
    try:
        User.update_following(data['userId1'], data['userId2'], "add")
        return jsonify({"success": True}), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@bp.route('/remove', methods=['DELETE'])
def unfollow_user():
    data = request.get_json()
    try:
        User.update_following(data['userId1'], data['userId2'], "remove")
        return jsonify({"success": True}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@bp.route('/following/<user_id>', methods=['GET'])
def get_following(user_id):
    user = User.find_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    following_details = []
    for following_id in user['following']:
        following_user = User.find_user_by_id(following_id)
        if following_user:
            spotify_id = following_user['spotify_id']
            user_details = spotipy.Spotify().user(spotify_id)
            following_details.append({
                "username": user_details['display_name'],
                "profile_picture": user_details['images'][0]['url'] if user_details['images'] else None
            })
    return jsonify({"success": True, "following": following_details}), 200

@bp.route('/followers/<user_id>', methods=['GET'])
def get_followers(user_id):
    user = User.find_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    followers_details = []
    for follower_id in user['followers']:
        follower_user = User.find_user_by_id(follower_id)
        if follower_user:
            spotify_id = follower_user['spotify_id']
            user_details = spotipy.Spotify().user(spotify_id)
            followers_details.append({
                "username": user_details['display_name'],
                "profile_picture": user_details['images'][0]['url'] if user_details['images'] else None
            })
    return jsonify({"success": True, "followers": followers_details}), 200

