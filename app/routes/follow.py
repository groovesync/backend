from flask import Blueprint, request, jsonify
from app.models.follow import Follow
import spotipy

bp = Blueprint('follow', __name__, url_prefix='/follow')

@bp.route('/add', methods=["POST"])
def follow_user():
    """
    Create a follow relationship between two users.
    
    Args:
        Request Body (JSON):
            - spotifyId1 (str): The Spotify ID of the user who wants to follow
            - spotifyId2 (str): The Spotify ID of the user to be followed
    
    Returns:
        JSON response with success status and follow data:
        - success (bool): True if operation successful
        - follow_id (str): ID of the created follow relationship
        - message (str): Error message if operation fails
    
    Status Codes:
        201: Follow relationship created successfully
        400: Bad request (invalid data or validation error)
    """
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
    """
    Remove a follow relationship between two users.
    
    Args:
        Query Parameters:
            - spotifyId1 (str): The Spotify ID of the user who wants to unfollow
            - spotifyId2 (str): The Spotify ID of the user to be unfollowed
    
    Returns:
        JSON response with success status:
        - success (bool): True if operation successful, False if no relationship found
        - message (str): Error message if operation fails
    
    Status Codes:
        201: Follow relationship removed successfully
        204: No follow relationship found to remove
        400: Bad request (invalid data or validation error)
    """
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
    """
    Get all users that a specific user is following.
    
    Args:
        spotify_id (str): The Spotify ID of the user whose following list to retrieve
    
    Headers:
        Spotify-Token (str): Spotify access token required for API calls
    
    Returns:
        JSON response with following data:
        - following (list): List of users being followed with enriched information:
            - user_id (str): Spotify user ID
            - user_display_name (str): User's display name
            - user_image (str): URL to user's profile image
        - following (null): If no following relationships exist
        - success (bool): False if operation fails
        - message (str): Error message if operation fails
        - error (str): Detailed error information if applicable
    
    Status Codes:
        200: Successfully retrieved following list
        401: Missing or invalid Spotify access token
        400: Error fetching user information from Spotify API
    """
    following = Follow.get_following(spotify_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    if following != []:
        enriched_following = []
        for follow in following:
            spotifyId = follow["spotifyId2"]
            sp = spotipy.Spotify(auth=spotify_access_token)
            try:
                user = sp.user(spotifyId)
                enriched_following.append({
                    "user_id": spotifyId,
                    "user_display_name": user["display_name"],
                    "user_image": user["images"][0]["url"] if user.get("images") and len(user["images"]) > 0 else None
                })
            except Exception as e:
                return jsonify({"success": False, "message": "Error fetching user information", "error": str(e)}), 400
        return jsonify({"following": enriched_following}), 200
    return jsonify({"following": None}), 200

@bp.route('/followers/<spotify_id>', methods=['GET'])
def get_followers(spotify_id):
    """
    Get all users that are following a specific user.
    
    Args:
        spotify_id (str): The Spotify ID of the user whose followers list to retrieve
    
    Headers:
        Spotify-Token (str): Spotify access token required for API calls
    
    Returns:
        JSON response with followers data:
        - followers (list): List of followers with enriched information:
            - user_id (str): Spotify user ID
            - user_display_name (str): User's display name
            - user_image (str): URL to user's profile image
        - followers (null): If no followers exist
        - success (bool): False if operation fails
        - message (str): Error message if operation fails
        - error (str): Detailed error information if applicable
    
    Status Codes:
        200: Successfully retrieved followers list
        401: Missing or invalid Spotify access token
        400: Error fetching user information from Spotify API
    """
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
                    "user_image": user["images"][0]["url"] if user.get("images") and len(user["images"]) > 0 else None
                })
            except Exception as e:
                return jsonify({"success": False, "message": "Error fetching user information", "error": str(e)}), 400
        return jsonify({"followers": enriched_followers}), 200
    return jsonify({"followers": None}), 200

