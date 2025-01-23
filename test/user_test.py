import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.user import bp
import jwt

class UserRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testsecret'
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

        self.valid_token = jwt.encode({"username": "testuser"}, self.app.config['SECRET_KEY'], algorithm="HS256")

    @patch("app.models.user.User.delete_user")
    def test_delete_account_success(self, mock_delete_user):
        mock_delete_user.return_value = True
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.delete("/user/delete", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "User 'testuser' deleted successfully")

    @patch("app.models.user.User.delete_user")
    def test_delete_account_not_found(self, mock_delete_user):
        mock_delete_user.return_value = False
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.delete("/user/delete", headers=headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "User not found or could not be deleted")

    @patch("app.models.user.User.find_user_by_credentials")
    @patch("app.models.user.User.update_password")
    def test_update_password_success(self, mock_update_password, mock_find_user):
        mock_find_user.return_value = True
        mock_update_password.return_value = True
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.put("/user/update-password", headers=headers, json={
            "old_password": "oldpass",
            "new_password": "newpass"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Password updated successfully")

    @patch("app.models.user.User.find_user_by_credentials")
    def test_update_password_wrong_old_password(self, mock_find_user):
        mock_find_user.return_value = False
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.put("/user/update-password", headers=headers, json={
            "old_password": "wrongoldpass",
            "new_password": "newpass"
        })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Old password is incorrect")

if __name__ == "__main__":
    unittest.main()