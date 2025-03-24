import jwt
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app.models.user import User
from app.utils.token_manager import TokenManager
from datetime import datetime, timedelta
import spotipy

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

@bp.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    spotify_id = data.get('spotify_id') 

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    if User.find_user_by_username(username):
        return jsonify({"success": False, "message": "User already exists"}), 400

    new_user = User(username=username, password=password, spotify_id=spotify_id)
    if new_user.save():
        expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
        token = jwt.encode({"username": username, "exp": expiration_time},
                           current_app.config['SECRET_KEY'], algorithm="HS256")

        refresh_token = jwt.encode({"username": username, "exp": datetime.utcnow() + timedelta(days=7)},
                                   current_app.config['SECRET_KEY'], algorithm="HS256")
        
        print(f"\n\n{token}\n\n{username}\n\n")
        TokenManager.store_refresh_token(username, refresh_token)

        return jsonify({
            "success": True,
            "message": f"User '{username}' created successfully",
            "user_info": {
                "username": username,
                "spotify_id": spotify_id,
            },
            "backend_token": token,
            "refresh_token": refresh_token
        }), 201
    else:
        return jsonify({"success": False, "message": "Could not create user"}), 500

@bp.route('/delete', methods=['DELETE'])
@token_required
def delete_account():
    username = request.user.get('username')

    if not username:
        return jsonify({"success": False, "message": "Could not identify the user from the token"}), 401

    user_deleted = User.delete_user(username)
    if user_deleted:
        TokenManager.invalidate_tokens_for_user(username)
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

@bp.route('/search', methods=['GET'])
@token_required
def search_users():
    query = request.args.get('q')
    spotify_access_token = request.headers.get('Spotify-Token')
    if not spotify_access_token:
        return jsonify({"success": False, "message": "Spotify access token required"}), 401
    
    sp = spotipy.Spotify(auth=spotify_access_token)
    try:
        users = User.search_users(query)
        if users["users"]:
            for user in users["users"]:
                userInfo = sp.user(user["spotify_id"])
                user["image"] = userInfo["images"][0]["url"]
            
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": "No users found"}), 404
    
@bp.route('/users', methods=['GET'])
@token_required
def get_all_users():
    try:
        users = User.get_all_users()
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "No users found"}), 404

