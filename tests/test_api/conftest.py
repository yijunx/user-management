import pytest
from app.app import app
from app.schemas.user import UserLoginWithPassword, UserRegisterWithPassword
from flask.testing import FlaskClient
from app.db.database import SessionLocal


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
