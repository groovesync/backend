import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.auth import bp
import pytest
import jwt
from datetime import datetime, timedelta


class AuthRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testsecret'
        self.app.config['JWT_EXPIRATION_SECONDS'] = 3600 
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

    @patch("app.models.user.User.find_user_by_credentials")
    def test_login_success(self, mock_find_user):
        mock_find_user.return_value = True
        response = self.client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        self.assertTrue(response.json["success"])

    @patch("app.models.user.User.find_user_by_credentials")
    def test_login_invalid_credentials(self, mock_find_user):
        mock_find_user.return_value = False
        response = self.client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid username or password")

    def test_login_missing_fields(self):
        response = self.client.post("/auth/login", json={
            "username": "testuser"
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Username and password required")

    @patch("app.models.user.User.save")
    def test_register_success(self, mock_save):
        mock_save.return_value = True
        response = self.client.post("/auth/register", json={
            "username": "newuser",
            "password": "newpass"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "User registered successfully")
        self.assertIn("token", response.json)

    @patch("app.models.user.User.save")
    def test_register_username_exists(self, mock_save):
        mock_save.return_value = False
        response = self.client.post("/auth/register", json={
            "username": "existinguser",
            "password": "testpass"
        })

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["message"], "Username already exists")


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testsecret'
    app.config['JWT_EXPIRATION_SECONDS'] = 3600
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    token = jwt.encode({
        'username': 'testuser',
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, 'testsecret', algorithm='HS256')
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

class TestAuthRoutes:
    def test_login_success(self, test_client):
        """Test successful login with valid credentials"""
        with patch('app.models.user.User.find_user_by_credentials') as mock_find:
            mock_find.return_value = {'username': 'testuser', 'password': 'hashed_password'}
            
            response = test_client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'password123'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'token' in data
            assert 'refresh_token' in data

    def test_login_missing_credentials(self, test_client):
        """Test login with missing credentials"""
        response = test_client.post('/auth/login', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Username and password required' in data['message']

    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials"""
        with patch('app.models.user.User.find_user_by_credentials') as mock_find:
            mock_find.return_value = None
            
            response = test_client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
            assert 'Invalid username or password' in data['message']

    def test_refresh_token_success(self, test_client):
        """Test successful token refresh"""
        refresh_token = jwt.encode({
            'username': 'testuser',
            'exp': datetime.utcnow() + timedelta(days=7)
        }, 'testsecret', algorithm='HS256')
        
        with patch('app.utils.persistence_manager.PersistenceManager.get_database') as mock_db:
            mock_db.return_value.refresh_tokens.find_one.return_value = {
                'refresh_token': refresh_token,
                'exp': datetime.utcnow() + timedelta(days=7)
            }
            
            response = test_client.post('/auth/refresh', json={
                'refresh_token': refresh_token
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'token' in data

    def test_refresh_token_invalid(self, test_client):
        """Test token refresh with invalid token"""
        response = test_client.post('/auth/refresh', json={
            'refresh_token': 'invalid_token'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid or expired refresh token' in data['message']

    def test_spotify_login_success(self, test_client):
        """Test successful Spotify login"""
        with patch('requests.post') as mock_post, \
             patch('requests.get') as mock_get, \
             patch('app.models.user.User.find_user_by_spotify_id') as mock_find, \
             patch('app.models.user.User.save') as mock_save:
            
            # Mock Spotify token response
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                'access_token': 'spotify_access_token',
                'refresh_token': 'spotify_refresh_token'
            }
            
            # Mock Spotify user info response
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'id': 'spotify_user_id',
                'display_name': 'Spotify User',
                'email': 'user@example.com',
                'followers': {'total': 100},
                'images': []
            }
            
            mock_find.return_value = None
            mock_save.return_value = True
            
            response = test_client.post('/auth/login/spotify', json={
                'code': 'spotify_auth_code'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'user_info' in data
            assert 'backend_token' in data
            assert 'spotify_access_token' in data

    def test_spotify_login_missing_code(self, test_client):
        """Test Spotify login with missing authorization code"""
        response = test_client.post('/auth/login/spotify', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Authorization code required' in data['message']

    def test_logout_success(self, test_client):
        """Test successful logout"""
        refresh_token = jwt.encode({
            'username': 'testuser',
            'exp': datetime.utcnow() + timedelta(days=7)
        }, 'testsecret', algorithm='HS256')
        
        with patch('app.utils.token_manager.TokenManager.delete_refresh_token') as mock_delete:
            mock_delete.return_value = True
            
            response = test_client.post('/auth/logout', json={
                'refresh_token': refresh_token
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'Logged out successfully' in data['message']

    def test_logout_missing_token(self, test_client):
        """Test logout with missing refresh token"""
        response = test_client.post('/auth/logout', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Refresh token required' in data['message']


if __name__ == "__main__":
    unittest.main()
