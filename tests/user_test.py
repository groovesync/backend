import pytest
from unittest.mock import patch, MagicMock
from app import create_app
import jwt
from datetime import datetime, timedelta

@pytest.fixture
def test_client():
    app = create_app()
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

class TestUserRoutes:
    def test_create_user_success(self, test_client):
        """Test successful user creation"""
        with patch('app.models.user.User.find_user_by_username') as mock_find, \
             patch('app.models.user.User.save') as mock_save:
            
            mock_find.return_value = None
            mock_save.return_value = True
            
            response = test_client.post('/user/create', json={
                'username': 'newuser',
                'password': 'password123',
                'spotify_id': 'spotify123'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert 'user_info' in data
            assert 'backend_token' in data
            assert 'refresh_token' in data

    def test_create_user_missing_fields(self, test_client):
        """Test user creation with missing required fields"""
        response = test_client.post('/user/create', json={
            'username': 'newuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Username and password are required' in data['message']

    def test_create_user_already_exists(self, test_client):
        """Test user creation with existing username"""
        with patch('app.models.user.User.find_user_by_username') as mock_find:
            mock_find.return_value = {'username': 'existinguser'}
            
            response = test_client.post('/user/create', json={
                'username': 'existinguser',
                'password': 'password123'
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'User already exists' in data['message']

    def test_delete_account_success(self, test_client, auth_headers):
        """Test successful account deletion"""
        with patch('app.models.user.User.delete_user') as mock_delete, \
             patch('app.utils.token_manager.TokenManager.invalidate_tokens_for_user') as mock_invalidate:
            
            mock_delete.return_value = True
            mock_invalidate.return_value = True
            
            response = test_client.delete('/user/delete', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'deleted successfully' in data['message']

    def test_delete_account_not_found(self, test_client, auth_headers):
        """Test account deletion for non-existent user"""
        with patch('app.models.user.User.delete_user') as mock_delete:
            mock_delete.return_value = False
            
            response = test_client.delete('/user/delete', headers=auth_headers)
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert 'User not found' in data['message']

    def test_update_password_success(self, test_client, auth_headers):
        """Test successful password update"""
        with patch('app.models.user.User.find_user_by_credentials') as mock_find, \
             patch('app.models.user.User.update_password') as mock_update:
            
            mock_find.return_value = {'username': 'testuser'}
            mock_update.return_value = True
            
            response = test_client.put('/user/update-password', 
                headers=auth_headers,
                json={
                    'old_password': 'oldpass',
                    'new_password': 'newpass'
                }
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'Password updated successfully' in data['message']

    def test_update_password_missing_fields(self, test_client, auth_headers):
        """Test password update with missing fields"""
        response = test_client.put('/user/update-password', 
            headers=auth_headers,
            json={
                'old_password': 'oldpass'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Old and new passwords are required' in data['message']

    def test_update_password_invalid_old_password(self, test_client, auth_headers):
        """Test password update with incorrect old password"""
        with patch('app.models.user.User.find_user_by_credentials') as mock_find:
            mock_find.return_value = None
            
            response = test_client.put('/user/update-password', 
                headers=auth_headers,
                json={
                    'old_password': 'wrongpass',
                    'new_password': 'newpass'
                }
            )
            
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
            assert 'Old password is incorrect' in data['message']

    def test_search_users_success(self, test_client, auth_headers):
        """Test successful user search"""
        with patch('app.models.user.User.search_users') as mock_search:
            mock_search.return_value = {
                'users': [
                    {'username': 'user1', 'spotify_id': 'spotify1'},
                    {'username': 'user2', 'spotify_id': 'spotify2'}
                ]
            }
            
            response = test_client.get('/user/search?q=user', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert len(data['data']['users']) == 2

    def test_search_users_not_found(self, test_client, auth_headers):
        """Test user search with no results"""
        with patch('app.models.user.User.search_users') as mock_search:
            mock_search.side_effect = Exception('No users found')
            
            response = test_client.get('/user/search?q=nonexistent', headers=auth_headers)
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert 'No users found' in data['message']

    def test_get_all_users_success(self, test_client, auth_headers):
        """Test successful retrieval of all users"""
        with patch('app.models.user.User.get_all_users') as mock_get:
            mock_get.return_value = {
                'users': [
                    {'username': 'user1', 'spotify_id': 'spotify1'},
                    {'username': 'user2', 'spotify_id': 'spotify2'}
                ]
            }
            
            response = test_client.get('/user/users', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert len(data['data']['users']) == 2

    def test_get_all_users_not_found(self, test_client, auth_headers):
        """Test retrieval of all users when none exist"""
        with patch('app.models.user.User.get_all_users') as mock_get:
            mock_get.side_effect = Exception('No users found')
            
            response = test_client.get('/user/users', headers=auth_headers)
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert 'No users found' in data['message']
