import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.review import bp
import jwt

class ReviewRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testsecret'
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

        self.valid_token = jwt.encode({"username": "testuser"}, self.app.config['SECRET_KEY'], algorithm="HS256")

    @patch("app.models.review.Review.save")
    def test_save_review_success(self, mock_save):
        mock_save.return_value = "review_id"
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.post("/review/save", headers=headers, json={
            "userId": "valid_user_id",
            "rate": 4,
            "text": "Great album!"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(response.json["review_id"], "review_id")

    @patch("app.models.review.Review.save")
    def test_save_review_invalid_user(self, mock_save):
        mock_save.side_effect = ValueError("Invalid user ID")
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.post("/review/save", headers=headers, json={
            "userId": "invalid_user_id",
            "rate": 4,
            "text": "Great album!"
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["success"], False)
        self.assertEqual(response.json["message"], "Invalid user ID")

    @patch("app.models.review.Review.save")
    def test_create_review_invalid_rate(self, mock_save):
        mock_save.side_effect = ValueError("Rate must be between 0 and 5")
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.post("/review/save", headers=headers, json={
            "userId": "valid_user_id",
            "rate": 6,
            "text": "Great album!"
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["success"], False)
        self.assertEqual(response.json["message"], "Rate must be between 0 and 5")

    @patch("app.models.review.Review.get_by_user")
    def test_get_reviews_success(self, mock_get_by_user):
        mock_get_by_user.return_value = [{"rate": 4, "text": "Great album!"}]
        response = self.client.get("/review/get/valid_user_id?limit=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(len(response.json["reviews"]), 1)

    @patch("app.models.review.Review.get_by_user")
    def test_get_reviews_invalid_user(self, mock_get_by_user):
        mock_get_by_user.return_value = []
        response = self.client.get("/review/get/invalid_user_id?limit=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertEqual(len(response.json["reviews"]), 0)

    @patch("app.models.review.Review.update")
    def test_update_review_success(self, mock_update):
        mock_update.return_value = True
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.put("/review/update/review_id", headers=headers, json={
            "rate": 5,
            "text": "Updated review"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)

    @patch("app.models.review.Review.update")
    def test_update_review_not_found(self, mock_update):
        mock_update.return_value = False
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.put("/review/update/invalid_review_id", headers=headers, json={
            "rate": 5,
            "text": "Updated review"
        })

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["success"], False)
        self.assertEqual(response.json["message"], "Review not found")

    @patch("app.models.review.Review.delete")
    def test_delete_review_success(self, mock_delete):
        mock_delete.return_value = True
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.delete("/review/delete/review_id", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)

    @patch("app.models.review.Review.delete")
    def test_delete_review_not_found(self, mock_delete):
        mock_delete.return_value = False
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.delete("/review/delete/invalid_review_id", headers=headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["success"], False)
        self.assertEqual(response.json["message"], "Review not found")

if __name__ == '__main__':
    unittest.main()
