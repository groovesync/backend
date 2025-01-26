import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
import requests
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
refresh_tokens = {} 

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    is_valid = User.find_user_by_credentials(username, password)
    if is_valid:
        expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
        token = jwt.encode(
            {"username": username, "exp": expiration_time},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {"username": username, "exp": datetime.utcnow() + timedelta(days=7)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        refresh_tokens[refresh_token] = username

        return jsonify({"success": True, "token": token, "refresh_token": refresh_token}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token required"}), 400

    try:
        payload = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        username = payload.get('username')

        if refresh_token not in refresh_tokens or refresh_tokens[refresh_token] != username:
            return jsonify({"success": False, "message": "Invalid refresh token"}), 401

        new_token = jwt.encode(
            {"username": username, "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": new_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid refresh token"}), 401


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = User(username, password)

    if user.save():
        expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
        token = jwt.encode(
            {"username": username, "exp": expiration_time},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {"username": username, "exp": datetime.utcnow() + timedelta(days=7)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        refresh_tokens[refresh_token] = username

        return jsonify({"success": True, "message": "User registered successfully", "token": token, "refresh_token": refresh_token}), 201
    else:
        return jsonify({"success": False, "message": "Username already exists"}), 409



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
    username = user_info["display_name"]

    existing_user = User.find_user_by_spotify_id(spotify_id)
    if existing_user:
        token = jwt.encode(
            {"username": existing_user["username"], "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": token}), 200
    
    new_user = User(username=username, spotify_id=spotify_id)
    new_user.save()

    token = jwt.encode(
        {"username": username, "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])},
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    return jsonify({"success": True, "token": token}), 201
