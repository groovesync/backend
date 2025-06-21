from flask import Blueprint, request, jsonify
from app.models.review import Review
from app.models.follow import Follow
import spotipy

bp = Blueprint('review', __name__, url_prefix='/review')

@bp.route('/save', methods=['POST'])
def save():
    """
    Save a new review for an album.
    
    Request body:
        userId (str): Spotify user ID of the reviewer
        rate (int): Rating from 0 to 5
        albumId (str): Spotify album ID
        text (str, optional): Review text content
        
    Returns:
        JSON response with:
            - success (bool): Whether the save was successful
            - review_id (str): ID of the created review (if successful)
            - message (str): Error message (if failed)
            
    Status codes:
        - 201: Review saved successfully
        - 400: Invalid data (invalid user ID, rating out of range, etc.)
    """
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
    """
    Get all reviews by a specific user with enriched album information.
    
    Path parameters:
        user_id (str): Spotify user ID to get reviews for
        
    Headers required:
        Spotify-Token: Valid Spotify access token
        
    Returns:
        JSON response with:
            - success (bool): Whether the request was successful
            - reviews (list): List of enriched review objects with album details
            - message (str): Error message (if failed)
            
    Review object structure:
        - album_id (str): Spotify album ID
        - album_name (str): Album title
        - album_url (str): Spotify album URL
        - album_image (str): Album cover image URL
        - release_year (str): Album release year
        - artists (list): List of artist objects with name and id
        - review_text (str): Review text content
        - rating (int): Review rating (0-5)
        
    Status codes:
        - 200: Reviews retrieved successfully
        - 401: Missing Spotify access token
        - 400: Error fetching album from Spotify
    """
    reviews = Review.get_by_user(user_id)
    reviews.reverse()
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
    """
    Update an existing review.
    
    Path parameters:
        review_id (str): ID of the review to update
        
    Request body:
        rate (int, optional): New rating from 0 to 5
        text (str, optional): New review text content
        
    Returns:
        JSON response with:
            - success (bool): Whether the update was successful
            - message (str): Error message (if failed)
            
    Status codes:
        - 200: Review updated successfully
        - 400: Invalid data (rating out of range, etc.)
        - 404: Review not found
    """
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
    """
    Delete a review.
    
    Path parameters:
        review_id (str): ID of the review to delete
        
    Returns:
        JSON response with:
            - success (bool): Whether the deletion was successful
            - message (str): Error message (if failed)
            
    Status codes:
        - 200: Review deleted successfully
        - 404: Review not found
    """
    success = Review.delete(review_id)
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Review not found"}), 404
    
@bp.route('/get-by-review-id/<review_id>')
def get_by_review_id(review_id):
    """
    Get a specific review by its ID with enriched album information.
    
    Path parameters:
        review_id (str): ID of the review to retrieve
        
    Headers required:
        Spotify-Token: Valid Spotify access token
        
    Returns:
        JSON response with:
            - review (dict): Review data
            - album_info (dict): Enriched album information
            - message (str): Error message (if failed)
            
    Album info structure:
        - name (str): Album title
        - artists (list): List of artist objects with name and id
        - image (str): Album cover image URL
        - release_year (str): Album release year
        - id (str): Spotify album ID
        
    Status codes:
        - 200: Review retrieved successfully
        - 401: Missing Spotify access token
        - 400: Error fetching album from Spotify
        - 404: Review not found
        - 204: Album not found on Spotify
    """
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
    """
    Get albums that are popular among the user's friends (people they follow).
    
    Query parameters:
        spotifyId (str): Spotify user ID to get friends' popular albums for
        
    Headers required:
        Spotify-Token: Valid Spotify access token
        
    Returns:
        JSON response with:
            - albums (list): List of popular albums from friends
            - message (str): Error message (if failed)
            
    Album object structure:
        - name (str): Album title
        - image (str): Album cover image URL
        - release_year (str): Album release year
        - id (str): Spotify album ID
        
    Status codes:
        - 200: Albums retrieved successfully
        - 401: Missing Spotify access token
        - 400: Error fetching album from Spotify
        - 204: No album found on Spotify
    """
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
