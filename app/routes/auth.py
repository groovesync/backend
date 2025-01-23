import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


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
        return jsonify({"success": True, "token": token}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


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
        return jsonify({"success": True, "message": "User registered successfully", "token": token}), 201
    else:
        return jsonify({"success": False, "message": "Username already exists"}), 409
