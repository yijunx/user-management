import pytest
from app.app import app
from app.exceptions.user import UserEmailAlreadyExist
from app.schemas.user import (
    UserInResponse,
    UserLoginWithPassword,
    UserRegisterWithPassword,
)
from flask.testing import FlaskClient
from app.db.database import SessionLocal
from app.util.process_request import encode_access_token
import app.service.user as userService
import os


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def client() -> FlaskClient:
    # temporarily disable csrf checks..
    app.config["WTF_CSRF_METHODS"] = []
    with app.test_client() as c:
        yield c


@pytest.fixture
def user_register_with_password() -> UserRegisterWithPassword:
    return UserRegisterWithPassword(
        name="tom_with_password", email="tom@tom.com", password="badpassword"
    )


@pytest.fixture
def user_login_with_password() -> UserLoginWithPassword:
    return UserLoginWithPassword(email="tom@tom.com", password="badpassword")


@pytest.fixture
def client_from_admin() -> FlaskClient:
    user = userService.get_user_with_email(email=os.getenv("ADMIN_USER_EMAIL"))
    user_in_response = UserInResponse(**user.dict())
    token = encode_access_token(user_in_reponse=user_in_response)
    with app.test_client() as c:
        c.set_cookie("localhost", "token", token)
        yield c


@pytest.fixture
def user_email() -> str:
    return "tester@google.com"


@pytest.fixture
def client_from_user(user_email: str) -> FlaskClient:
    try:
        user = userService.create_user_with_google_login(
            name="tester", email=user_email
        )
    except UserEmailAlreadyExist:
        user = userService.get_user_with_email(email=user_email)
    user_in_response = UserInResponse(**user.dict())
    token = encode_access_token(user_in_reponse=user_in_response)
    with app.test_client() as c:
        c.set_cookie("localhost", "token", token)
        yield c
