from unittest.mock import patch
from app.schemas.user import (
    UserLoginWithPassword,
    UserRegisterWithPassword,
    UserInResponse,
)
import app.repo.user as userRepo
from tests import fixture
from flask.testing import FlaskClient
from sqlalchemy.orm import Session


GOOGLE_LOGIN_USER_ID = ""
PASSWORD_LOGIN_USER_ID = ""


@patch(
    "app.blueprints.core.get_google_user_from_request",
    return_value=fixture.fake_google_user(),
)
def test_login_with_user_creation_with_google(
    mock_get_google_user_from_request, client: FlaskClient
):
    r = client.post("/api/login_with_google", headers={"Authorization": "Bearer token"})
    user_in_response = UserInResponse(**r.get_json()["response"])
    global GOOGLE_LOGIN_USER_ID
    GOOGLE_LOGIN_USER_ID = user_in_response.id
    assert r.status_code == 200
    assert user_in_response.name == fixture.fake_google_user().name


@patch(
    "app.blueprints.core.get_google_user_from_request",
    return_value=fixture.fake_google_user(),
)
def test_login_without_user_creation_with_google(
    mock_get_google_user_from_request, client: FlaskClient
):
    r = client.post("/api/login_with_google", headers={"Authorization": "Bearer token"})
    user_in_response = UserInResponse(**r.get_json()["response"])
    assert r.status_code == 200
    assert user_in_response.name == fixture.fake_google_user().name


def test_register_user_with_password(
    client: FlaskClient, user_register_with_password: UserRegisterWithPassword
):
    r = client.post("/api/register", json=user_register_with_password.dict())
    user_in_response = UserInResponse(**r.get_json()["response"])
    global PASSWORD_LOGIN_USER_ID
    PASSWORD_LOGIN_USER_ID = user_in_response.id
    assert r.status_code == 201
    assert user_in_response.name == user_register_with_password.name


def test_login_user_with_password(
    client: FlaskClient, user_login_with_password: UserLoginWithPassword
):
    r = client.post("/api/login", json=user_login_with_password.dict())
    user_in_response = UserInResponse(**r.get_json()["response"])
    assert r.status_code == 200
    assert user_in_response.id == PASSWORD_LOGIN_USER_ID


def test_delete_item(db: Session):
    userRepo.delete(db=db, item_id=GOOGLE_LOGIN_USER_ID)
    userRepo.delete(db=db, item_id=PASSWORD_LOGIN_USER_ID)
