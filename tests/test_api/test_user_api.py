from unittest.mock import patch
from app.schemas.user import (
    UserInLinkVerification,
    UserLoginWithPassword,
    UserRegisterWithPassword,
    UserInResponse,
    UserWithPaging,
)
import app.repo.user as userRepo
from tests import fixture
from flask.testing import FlaskClient
from sqlalchemy.orm import Session
from app.util.process_request import encode_email_verification_token
from app.service.user import get_user_with_email
import os


GOOGLE_LOGIN_USER_ID = ""
PASSWORD_LOGIN_USER_ID = ""
EMAIL_VERIFICATION_TOKEN = ""


# @patch("app.blueprints.usre.send_email_verification")
# def test_login_with_user_creation_with_google(
#     client: FlaskClient
# ):
#     r = client.post("/api/login_with_google", headers={"Authorization": "Bearer token"})
#     user_in_response = UserInResponse(**r.get_json()["response"])
#     global GOOGLE_LOGIN_USER_ID
#     GOOGLE_LOGIN_USER_ID = user_in_response.id
#     assert r.status_code == 200
#     assert user_in_response.name == fixture.fake_google_user().name


def test_list_users_from_admin(client_from_admin: FlaskClient):
    r = client_from_admin.get(f"/api/users?name={os.getenv('ADMIN_USER_NAME')}")
    print(r.data)
    assert r.status_code == 200
    users_with_paging = UserWithPaging(**r.get_json()["response"])


def test_list_users_from_user(client_from_user: FlaskClient):
    r = client_from_user.get(f"/api/users")
    assert r.status_code == 403


def test_get_user_from_user(client_from_user: FlaskClient, user_email: str):
    user = get_user_with_email(email=user_email)
    r = client_from_user.get(f"/api/users/{user.id}")
    user_in_response = UserInResponse(**r.get_json()["response"])
    assert r.status_code == 200
    assert user_in_response.name == user.name


def test_patch_user_from_user(client_from_user: FlaskClient, user_email: str):
    user = get_user_with_email(email=user_email)
    new_name = "new_name"
    r = client_from_user.patch(f"/api/users/{user.id}", json={"name": new_name})
    user_in_response = UserInResponse(**r.get_json()["response"])
    assert r.status_code == 200
    assert user_in_response.name == new_name


# def test_delete_user_from_user(client_from_user: FlaskClient, user_email: str):
#     user = get_user_with_email(email=user_email)
#     r = client_from_user.delete(f"/api/users/{user.id}")
#     assert r.status_code == 403

def test_ban_user_from_admin(client_from_admin: FlaskClient, user_email: str):
    user = get_user_with_email(email=user_email)
    r = client_from_admin.post(f"/api/users/{user.id}/ban")
    assert r .status_code == 200


def test_unban_user_from_admin(client_from_admin: FlaskClient, user_email: str):
    user = get_user_with_email(email=user_email)
    r = client_from_admin.post(f"/api/users/{user.id}/unban")
    assert r .status_code == 200



def test_delete_user_from_admin(client_from_admin: FlaskClient, user_email: str):
    user = get_user_with_email(email=user_email)
    r = client_from_admin.delete(f"/api/users/{user.id}")
    assert r.status_code == 200
