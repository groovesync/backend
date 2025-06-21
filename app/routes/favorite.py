from flask import Blueprint, request, jsonify
from app.models.favorite import Favorite
import spotipy

bp = Blueprint('favorite', __name__, url_prefix='/favorite')

@bp.route('/save', methods=["POST"])
def save():
    """
    Save a new favorite album for a user.
    
    Request body:
        userId (str): Spotify user ID of the user
        albumId (str): Spotify album ID to favorite
        
    Returns:
        JSON response with:
            - success (bool): Whether the save was successful
            - favorite_id (str): ID of the created favorite (if successful)
            - message (str): Error message (if failed)
            
    Status codes:
        - 201: Favorite saved successfully
        - 400: Invalid data (invalid user ID, etc.)
    """
    data = request.get_json()
    try:
        favorite = Favorite(
            user_id=data["userId"],
            album_id=data["albumId"]
        )
        favorite_id = favorite.save()
        return jsonify({"success": True, "favorite_id": str(favorite_id)}), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@bp.route('/get/<user_id>', methods=['GET'])
def get(user_id):
    """
    Get all favorite albums for a specific user with enriched album information.
    
    Path parameters:
        user_id (str): Spotify user ID to get favorites for
        
    Headers required:
        Spotify-Token: Valid Spotify access token
        
    Returns:
        JSON response with:
            - success (bool): Whether the request was successful
            - favorites (list): List of enriched favorite album objects
            - message (str): Error message (if failed)
            
    Favorite album object structure:
        - album_id (str): Spotify album ID
        - album_name (str): Album title
        - album_url (str): Spotify album URL
        - album_image (str): Album cover image URL
        - release_year (str): Album release year
        - artists (list): List of artist objects with name and id
        
    Status codes:
        - 200: Favorites retrieved successfully
        - 401: Missing Spotify access token
        - 400: Error fetching album from Spotify
    """
    favorites = Favorite.get_by_user(user_id)

    if not favorites:
        return jsonify({"success": False, "message": "No favorites found", "favorites": []}), 200

    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    enriched_favorites = []

    for favorite in favorites:
        try:
            album = sp.album(favorite["albumId"])
            if not album:
                continue 
        except Exception as e:
            return jsonify({"success": False, "message": "Error fetching album", "error": str(e)}), 400

        enriched_favorites.append({
            "album_id": album["id"],
            "album_name": album["name"],
            "album_url": album["external_urls"]["spotify"],
            "album_image": album["images"][0]["url"] if album["images"] else None,
            "release_year": album["release_date"][:4],
            "artists": [{"name": artist["name"], "id": artist["id"]} for artist in album["artists"]],
        })

    if not enriched_favorites:
        return jsonify({"success": False, "message": "No favorites found", "favorites": []}), 200

    return jsonify({"success": True, "favorites": enriched_favorites}), 200

@bp.route('/delete/<favorite_id>', methods=['DELETE'])
def delete(favorite_id):
    """
    Delete a favorite album.
    
    Path parameters:
        favorite_id (str): ID of the favorite to delete
        
    Returns:
        JSON response with:
            - success (bool): Whether the deletion was successful
            - message (str): Error message (if failed)
            
    Status codes:
        - 200: Favorite deleted successfully
        - 404: Favorite not found
    """
    success = Favorite.delete(favorite_id)
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Favorite not found"}), 404