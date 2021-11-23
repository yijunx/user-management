from unittest.mock import patch
from app.schemas.user import (
    UserInLinkVerification,
    UserLoginWithPassword,
    UserRegisterWithPassword,
    UserInResponse,
)
import app.repo.user as userRepo
import app.repo.casbin as casbinRepo
from tests import fixture
from flask.testing import FlaskClient
from sqlalchemy.orm import Session
from app.util.process_request import encode_email_verification_token
from app.casbin.resource_id_converter import get_resource_id_from_user_id


GOOGLE_LOGIN_USER_ID = ""
PASSWORD_LOGIN_USER_ID = ""
EMAIL_VERIFICATION_TOKEN = ""


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


@patch("app.service.user.celery.send_task")
def test_register_user_with_password(
    mock_send_task,
    client: FlaskClient,
    user_register_with_password: UserRegisterWithPassword,
    db: Session,
):
    r = client.post("/api/register", json=user_register_with_password.dict())
    user_in_response = UserInResponse(**r.get_json()["response"])
    global PASSWORD_LOGIN_USER_ID
    PASSWORD_LOGIN_USER_ID = user_in_response.id
    user_in_db = userRepo.get(db=db, item_id=user_in_response.id)
    global EMAIL_VERIFICATION_TOKEN
    EMAIL_VERIFICATION_TOKEN = encode_email_verification_token(
        user_in_email_verification=UserInLinkVerification(
            **user_in_response.dict(), salt=user_in_db.salt
        )
    )
    assert r.status_code == 201
    assert user_in_response.name == user_register_with_password.name


def test_register_same_user_with_password(
    client: FlaskClient, user_register_with_password: UserRegisterWithPassword
):
    r = client.post("/api/register", json=user_register_with_password.dict())
    assert r.status_code == 409
    assert r.get_json()["success"] == False


def test_login_user_with_password_without_email_verified(
    client: FlaskClient, user_login_with_password: UserLoginWithPassword
):
    r = client.post("/api/login", json=user_login_with_password.dict())
    # user_in_response = UserInResponse(**r.get_json()["response"])
    assert r.status_code == 200  # well now we allow user login without email verified..
    # assert user_in_response.id == PASSWORD_LOGIN_USER_ID


def test_verify_user_email(client: FlaskClient, db: Session):
    r = client.get(
        "/api/email_verification", query_string={"token": EMAIL_VERIFICATION_TOKEN}
    )
    print(r.get_data())
    user_in_db = userRepo.get(db=db, item_id=PASSWORD_LOGIN_USER_ID)
    assert user_in_db.email_verified == True


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
    casbinRepo.delete_policies_by_resource_id(
        db=db, resource_id=get_resource_id_from_user_id(item_id=GOOGLE_LOGIN_USER_ID)
    )
    casbinRepo.delete_policies_by_resource_id(
        db=db, resource_id=get_resource_id_from_user_id(item_id=PASSWORD_LOGIN_USER_ID)
    )
