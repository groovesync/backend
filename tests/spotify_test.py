import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.spotify import bp
from app.services.spotify import SpotipyClient
import jwt
from flask import json

class SpotifyRoutesTest(unittest.TestCase): 
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testsecret'
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()
        
        self.valid_token = jwt.encode({"username": "testuser"}, self.app.config['SECRET_KEY'], algorithm="HS256")
    
    @patch.object(SpotipyClient, 'get_saved_albums', return_value=[{"name": "Album 1"}, {"name": "Album 2"}, {"name": "Album 3"}, {"name": "Album 4"}])
    def test_get_saved_albums(self, mock_method):
        mock_method
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.get('/spotify/saved-albums?limit=4', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(len(response.json['data']), 4)
        mock_method.assert_called_once_with(4,0)
        
    @patch.object(SpotipyClient, 'get_saved_albums', side_effect=Exception("Spotify API error"))
    def test_get_saved_albums_api_failure(self, mock_method):
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.get('/spotify/saved-albums?limit=4', headers=headers)
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

    @patch.object(SpotipyClient, 'search_artists_albums', return_value = {"artists": [{"name": "Eminem", "id": "7dGJo4pcD2V6oG8kP0tJRR", "image": "https://example.com/eminem.jpg"}, {"name": "Drake", "id": "456", "image": "https://example.com/drake.jpg"}], "albums": [{"name": "The Eminem Show", "id":"2cWBwpqMsDJC1ZUwz813lo", "release_date": "2002-05-26", "total_tracks":20,"image": "https://i.scdn.co/image/ab67616d0000b2736ca5c90113b30c3c43ffb8f4"}, {"name": "Eminem Album", "id":"2cWBwpqMsDJC1ZUwz813lo", "release_date": "2002-05-26", "total_tracks":20,"image": "https://i.scdn.co/image/ab67616d0000b2736ca5c90113b30c3c43ffb8f4"}]})
    def test_search_artists_success(self, mock_method):
        response = self.client.get('/spotify/search/?q=Eminem&limit=2', headers={"Authorization": self.token})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["artists"]), 2)
        self.assertEqual(len(data["albums"]), 2)
        self.assertEqual(data["artists"][0]["name"], "Eminem")
        mock_method.assert_called_once_with(4,0)

    @patch.object(SpotipyClient, 'search_artists_albums')
    def test_search_artists_and_albums_missing_query(self):
        response = self.client.get('/spotify/search/', headers={"Authorization": self.token})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("Query parameter 'q' is required", data["message"])

    @patch.object(SpotipyClient, 'search_albums', return_value = {"albums": [{"name": "The Eminem Show", "id":"2cWBwpqMsDJC1ZUwz813lo", "release_date": "2002-05-26", "total_tracks":20,"image": "https://i.scdn.co/image/ab67616d0000b2736ca5c90113b30c3c43ffb8f4"}, {"name": "Eminem Album", "id":"2cWBwpqMsDJC1ZUwz813lo", "release_date": "2025-02-12", "total_tracks":9,"image": "https://i.scdn.co/image/ab67616d0000b2736ca5c90113b30c3c43ffb8f4"}]})
    def test_search_artists_empty_result(self, mock_method):
        response = self.client.get('/spotify/search/albums/?q=Eminem', headers={"Authorization": self.token})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["albums"][0]["name"], "The Eminem Show")
        self.assertEqual(data["albums"][2]["name"], "Eminem Album")
    
    @patch.object(SpotipyClient, 'search_albums')
    def test_search_albums_missing_query(self):
        response = self.client.get('/spotify/search/albums/', headers={"Authorization": self.token})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("Query parameter 'q' is required", data["message"])

if __name__ == "__main__":
    unittest.main()
