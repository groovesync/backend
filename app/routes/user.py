import jwt
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app.models.user import User

bp = Blueprint('user', __name__, url_prefix='/user')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Token is missing or invalid"}), 401

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = payload  
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


@bp.route('/delete', methods=['DELETE'])
@token_required
def delete_account():

    username = request.user.get('username')  

    if not username:
        return jsonify({"success": False, "message": "Could not identify the user from the token"}), 401

    user_deleted = User.delete_user(username)
    if user_deleted:
        return jsonify({"success": True, "message": f"User '{username}' deleted successfully"}), 200
    else:
        return jsonify({"success": False, "message": "User not found or could not be deleted"}), 404


@bp.route('/update-password', methods=['PUT'])
@token_required
def update_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    username = request.user.get('username')

    if not old_password or not new_password:
        return jsonify({"success": False, "message": "Old and new passwords are required"}), 400

    if not User.find_user_by_credentials(username, old_password):
        return jsonify({"success": False, "message": "Old password is incorrect"}), 401

    password_updated = User.update_password(username, new_password)
    if password_updated:
        return jsonify({"success": True, "message": "Password updated successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Could not update the password"}), 500
