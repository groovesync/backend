import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.auth import bp


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


if __name__ == "__main__":
    unittest.main()
