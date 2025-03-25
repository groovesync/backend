from flask import Blueprint, request, jsonify
from app.models.favorite import Favorite
import spotipy

bp = Blueprint('favorite', __name__, url_prefix='/favorite')

@bp.route('/save', methods=["POST"])
def save():
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
    favorites = Favorite.get_by_user(user_id)
    favorites.sort(reverse=True)

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
    success = Favorite.delete(favorite_id)
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Favorite not found"}), 404