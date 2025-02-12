import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
import requests
from app.models.user import User
from app.utils.persistence_manager import PersistenceManager
from app.__init__ import limiter
from app.utils.token_manager import TokenManager

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = User.find_user_by_credentials(username, password)
    if user:
        expiration_time = datetime.utcnow(
        ) + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
        token = jwt.encode({"username": username, "exp": expiration_time},
                           current_app.config['SECRET_KEY'], algorithm="HS256")
        refresh_token = jwt.encode({"username": username, "exp": datetime.utcnow(
        ) + timedelta(days=7)}, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        # Usando TokenManager para armazenar o refresh token
        TokenManager.store_refresh_token(username, refresh_token)
        
        return jsonify({"success": True, "token": token, "refresh_token": refresh_token}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token required"}), 400

    TokenManager.cleanup_expired_tokens()  # Usando TokenManager para limpar tokens expirados
    db = PersistenceManager.get_database()
    stored_token = db.refresh_tokens.find_one(
        {"refresh_token": refresh_token, "exp": {"$gte": datetime.utcnow()}})

    if not stored_token:
        return jsonify({"success": False, "message": "Invalid or expired refresh token"}), 401

    payload = jwt.decode(
        refresh_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    username = payload.get('username')
    new_token = jwt.encode({"username": username, "exp": datetime.utcnow(
    ) + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])}, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({"success": True, "token": new_token}), 200


@bp.route('/login/spotify', methods=['POST'])
def login_spotify():
    data = request.get_json()
    authorization_code = data.get('code')
    if not authorization_code:
        return jsonify({"success": False, "message": "Authorization code required"}), 400

    spotify_token_url = "https://accounts.spotify.com/api/token"
    redirect_uri = current_app.config['SPOTIFY_REDIRECT_URI']
    client_id = current_app.config['SPOTIFY_CLIENT_ID']
    client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']

    response = requests.post(
        spotify_token_url,
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )

    if response.status_code != 200:
        return jsonify({"success": False, "message": "Failed to authenticate with Spotify"}), 400

    spotify_data = response.json()
    access_token = spotify_data.get("access_token")
    refresh_token = spotify_data.get("refresh_token")

    if not access_token:
        return jsonify({"success": False, "message": "Failed to retrieve Spotify access token"}), 400

    user_info_response = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if user_info_response.status_code != 200:
        return jsonify({"success": False, "message": "Failed to retrieve Spotify user information"}), 400

    user_info = user_info_response.json()
    spotify_id = user_info["id"]
    username = user_info.get("display_name", spotify_id)

    existing_user = User.find_user_by_spotify_id(spotify_id)
    if existing_user:
        username = existing_user["username"]
    else:
        new_user = User(username=username, spotify_id=spotify_id)
        new_user.save()

    expiration_time = datetime.utcnow(
    ) + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
    backend_token = jwt.encode({"username": username, "exp": expiration_time},
                               current_app.config['SECRET_KEY'], algorithm="HS256")

    # Usando TokenManager para armazenar o refresh token
    TokenManager.store_refresh_token(username, refresh_token)

    response_data = {
        "success": True,
        "user_info": {
            "username": username,
            "spotify_id": spotify_id,
            "email": user_info.get("email"),
            "followers": user_info.get("followers", {}).get("total"),
            "images": user_info.get("images"),
        },
        "backend_token": backend_token,
        "spotify_access_token": access_token
    }

    return jsonify(response_data), 200


@bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token required"}), 400

    # Usando TokenManager para deletar o refresh token
    TokenManager.delete_refresh_token(refresh_token)
    
    return jsonify({"success": True, "message": "Logged out successfully"}), 200