from flask import Blueprint, request, jsonify
from app.models.review import Review

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
    except KeyError:
        return jsonify({"success": False, "message": "Missing required fields: userId, rate, albumId."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred while saving the review."}), 500

@bp.route('/get/<user_id>', methods=['GET'])
def get(user_id):
    try:
        limit = int(request.args.get('limit', 10))
        reviews = Review.get_by_user(user_id, limit)
        return jsonify({"success": True, "reviews": reviews}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred while fetching reviews."}), 500

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
            return jsonify({"success": False, "message": "Review not found or no changes made"}), 404
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred while updating the review."}), 500

@bp.route('/delete/<review_id>', methods=['DELETE'])
def delete(review_id):
    try:
        success = Review.delete(review_id)
        if success:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Review not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred while deleting the review."}), 500