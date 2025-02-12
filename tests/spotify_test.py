import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.spotify import bp
from app.services.spotify import SpotipyClient
import jwt

class SpotifyRoutesTest(unittest.TestCase): 
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testsecret'
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()
        self.valid_token = jwt.encode({"username": "testuser"}, self.app.config['SECRET_KEY'], algorithm="HS256")
    
    @patch.object(SpotipyClient, 'get_saved_albums', return_value=[{"name": "Album 1"}, {"name": "Album 2"}, {"name": "Album 3"}, {"name": "Album 4"}])
    def test_get_saved_albums(self, mock_method):
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


if __name__ == "__main__":
    unittest.main()
