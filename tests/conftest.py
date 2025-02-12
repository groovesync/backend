import pytest
from app import create_app
from app.services.spotify import SpotipyClient 

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testsecret'
    
    with app.app_context():
        with app.test_client() as client:
            yield client

    def spotipy_client():
        with app.app_context(): 
            client = SpotipyClient()
            yield client