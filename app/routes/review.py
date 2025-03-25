from flask import Blueprint, request, jsonify
from app.models.review import Review
from app.models.follow import Follow
import spotipy

bp = Blueprint('review', __name__, url_prefix='/review')

@bp.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    try:
        review = Review(
            user_id=data['userId'],
            rate=data['rate'],
            album_id=data['albumId'],
            text=data.get('text')
        )
        review_id = review.save()
        return jsonify({"success": True, "review_id": str(review_id)}), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@bp.route('/get/<user_id>', methods=['GET'])
def get(user_id):
    reviews = Review.get_by_user(user_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    sp = spotipy.Spotify(auth=spotify_access_token)
    enriched_reviews = []
    for review in reviews:
        try:
            album = sp.album(review["albumId"])
            if not album:
                continue
        except Exception as e:
            return jsonify({"success": False, "message": "Error fetching album", "error": str(e)}), 400

        enriched_reviews.append({
            "album_id": album["id"],
            "album_name": album["name"],
            "album_url": album["external_urls"]["spotify"],
            "album_image": album["images"][0]["url"] if album["images"] else None,
            "release_year": album["release_date"][:4],
            "artists": [{"name": artist["name"], "id": artist["id"]} for artist in album["artists"]],
            "review_text": review["text"],
            "rating": review["rate"],
            
        })

    if enriched_reviews == []:
        return jsonify({"success": False, "message": "No reviews found", "reviews": []}), 200

    return jsonify({"success": True, "reviews": enriched_reviews}), 200

@bp.route('/update/<review_id>', methods=['PUT'])
def update(review_id):
    data = request.get_json()
    try:
        success = Review.update(
            review_id,
            rate=data.get('rate'),
            text=data.get('text')
        )
        if success:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Review not found"}), 404
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@bp.route('/delete/<review_id>', methods=['DELETE'])
def delete(review_id):
    success = Review.delete(review_id)
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Review not found"}), 404
    
@bp.route('/get-by-review-id/<review_id>')
def get_by_review_id(review_id):
    review = Review.get_by_review_id(review_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401

    
    if review:
        sp = spotipy.Spotify(auth=spotify_access_token)
        try:
            album = sp.album(review["albumId"])
        except Exception as e:
            return jsonify({"success": False, "message": "Error fetching album", "error": str(e)}), 400

        if album is None:
            return jsonify({"success": False, "message": "No album found"}), 204

        album_name = album['name']
        artists = [{"name": artist['name'], "id": artist["id"]} for artist in album['artists']]
        album_image = album["images"][0]["url"]
        release_year = album['release_date'][:4]
        album_id = album['id']
            
        return jsonify({"review": review, 
                        "album_info": {
                            "name": album_name,
                            "artists": artists,
                            "image": album_image,
                            "release_year": release_year,
                            "id": album_id
                        }}), 200
    else:
        return jsonify({"review": None}), 404

@bp.route('/popular-with-friends', methods=['GET'])
def get_popular_with_friends():
    spotify_id = request.args.get('spotifyId', default="", type=str)

    following = Follow.get_following(spotify_id)
    spotify_access_token = request.headers.get('Spotify-Token')

    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    popular = []
    if following:
        for follow in following:
            following_spotify_id = follow["spotifyId2"]
            reviews = Review.get_by_user_spotify_id(following_spotify_id)
            if reviews:
                review = reviews[-1]

                sp = spotipy.Spotify(auth=spotify_access_token)
                try:
                    album = sp.album(review["albumId"])
                except Exception as e:
                    return jsonify({"success": False, "message": "Error fetching album", "error": str(e)}), 400

                if album is None:
                    return jsonify({"success": False, "message": "No album found"}), 204

                album_name = album['name']
                album_image = album["images"][0]["url"]
                release_year = album['release_date'][:4]
                album_id = album['id']

                popular.append({
                    "name": album_name,
                    "image": album_image,
                    "release_year": release_year,
                    "id": album_id
                })
    return jsonify({"albums": popular}), 200
