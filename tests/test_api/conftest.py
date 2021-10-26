import pytest
from app.app import app
import jwt
from flask.testing import FlaskClient


@pytest.fixture
def client() -> FlaskClient:
    # temporarily disable csrf checks..
    app.config['WTF_CSRF_METHODS'] = []
    with app.test_client() as c:
        yield c
