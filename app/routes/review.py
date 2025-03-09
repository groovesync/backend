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

@bp.route('/get/<user_id>', methods=['GET'])
def get(user_id):
    limit = int(request.args.get('limit', 1))
    reviews = Review.get_by_user(user_id, limit)
    return jsonify({"success": True, "reviews": reviews}), 200

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

