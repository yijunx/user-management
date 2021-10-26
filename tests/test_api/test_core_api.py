from unittest.mock import patch
from tests import fixture
from flask.testing import FlaskClient


@patch(
    "app.blueprints.core.get_google_user_from_request",
    return_value=fixture.fake_google_user(),
)
def test_login_with_google(mock_get_google_user_from_request, client: FlaskClient):
    r = client.post("/api/login_with_google", headers={"Authorization": "Bearer token"})
    print(r.get_json())
    print(r.get_data())
    assert r.status_code == 200
