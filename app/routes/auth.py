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
    """
    Authenticate a user with username and password.
    
    Request body:
        username (str): User's username
        password (str): User's password
        
    Returns:
        JSON response with:
            - success (bool): Whether the login was successful
            - token (str): JWT token for authentication
            - refresh_token (str): Token for refreshing the JWT
            - message (str): Error message if login fails
            
    Status codes:
        - 200: Login successful
        - 400: Missing username or password
        - 401: Invalid credentials
        - 500: Internal server error
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    try:
        user = User.find_user_by_credentials(username, password)
        if user:
            expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
            token = jwt.encode({"username": username, "exp": expiration_time},
                               current_app.config['SECRET_KEY'], algorithm="HS256")
            refresh_token = jwt.encode({"username": username, "exp": datetime.utcnow() + timedelta(days=7)},
                                       current_app.config['SECRET_KEY'], algorithm="HS256")
            
            TokenManager.store_refresh_token(username, refresh_token)
            
            return jsonify({"success": True, "token": token, "refresh_token": refresh_token}), 200
        else:
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred during login."}), 500


@bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh an expired JWT token using a refresh token.
    
    Request body:
        refresh_token (str): Valid refresh token
        
    Returns:
        JSON response with:
            - success (bool): Whether the refresh was successful
            - token (str): New JWT token
            - message (str): Error message if refresh fails
            
    Status codes:
        - 200: Token refreshed successfully
        - 400: Missing refresh token
        - 401: Invalid or expired refresh token
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token required"}), 400

    try:
        TokenManager.cleanup_expired_tokens()
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
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid refresh token"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred while refreshing the token."}), 500


@bp.route('/login/spotify', methods=['POST'])
async def login_spotify():  # Transformado em async def
    """
    Authenticate a user using Spotify OAuth.
    
    Request body:
        code (str): Authorization code from Spotify
        
    Returns:
        JSON response with:
            - success (bool): Whether the login was successful
            - user_info (dict): User information from Spotify
            - backend_token (str): JWT token for authentication
            - spotify_access_token (str): Token for Spotify API
            - message (str): Error message if login fails
            
    Status codes:
        - 200: Login successful
        - 400: Missing code or Spotify authentication failed
        - 500: Internal server error or communication failure with Spotify
    """
    data = request.get_json()
    authorization_code = data.get('code')
    if not authorization_code:
        return jsonify({"success": False, "message": "Authorization code required"}), 400

    try:
        spotify_token_url = "https://accounts.spotify.com/api/token"
        redirect_uri = current_app.config['SPOTIFY_REDIRECT_URI']
        client_id = current_app.config['SPOTIFY_CLIENT_ID']
        client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']

        async with httpx.AsyncClient() as client:
            # Usando httpx para a chamada assíncrona
            response = await client.post(
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
                return jsonify({"success": False, "message": "Failed to exchange authorization code with Spotify."}), 400

            spotify_data = response.json()
            access_token = spotify_data.get("access_token")
            refresh_token = spotify_data.get("refresh_token")

            if not access_token:
                return jsonify({"success": False, "message": "Failed to retrieve Spotify access token"}), 400

            # Segunda chamada de rede com httpx
            user_info_response = await client.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )

        if user_info_response.status_code != 200:
            return jsonify({"success": False, "message": "Failed to retrieve Spotify user information"}), 400

        user_info = user_info_response.json()
        spotify_id = user_info["id"]
        username = user_info.get("display_name", spotify_id)
        
        # Operações de DB (bloqueantes) são executadas em uma thread separada
        existing_user = await asyncio.to_thread(User.find_user_by_spotify_id, spotify_id)
        
        if existing_user:
            username = existing_user["username"]
        else:
            new_user = User(username=username, spotify_id=spotify_id)
            # Executando o save (bloqueante) em outra thread
            success = await asyncio.to_thread(new_user.save)
            if not success:
                return jsonify({"success": False, "message": "Could not create new user from Spotify data."}), 500

        expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_SECONDS'])
        backend_token = jwt.encode({"username": username, "exp": expiration_time},
                                   current_app.config['SECRET_KEY'], algorithm="HS256")

        await asyncio.to_thread(TokenManager.store_refresh_token, username, refresh_token)

        response_data = {
            "success": True,
            "user_info": {
                "username": username,
                "spotify_id": spotify_id,
                "email": user_info.get("email"),
                "followers": user_info.get("followers", {}).get("total"),
                "images": user_info.get("images") if user_info.get("images") else None,
            },
            "backend_token": backend_token,
            "spotify_access_token": access_token
        }
        return jsonify(response_data), 200

    except httpx.RequestError as e:
        return jsonify({"success": False, "message": f"Network error communicating with Spotify: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An internal error occurred during Spotify login: {e}"}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out a user by invalidating their refresh token.
    
    Request body:
        refresh_token (str): Refresh token to invalidate
        
    Returns:
        JSON response with:
            - success (bool): Whether the logout was successful
            - message (str): Success or error message
            
    Status codes:
        - 200: Logout successful
        - 400: Missing refresh token
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token required"}), 400

    try:
        TokenManager.delete_refresh_token(refresh_token)
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "An internal error occurred during logout."}), 500