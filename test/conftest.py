import pytest
from app import create_app

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testsecret'
    with app.test_client() as client:
        yield client
