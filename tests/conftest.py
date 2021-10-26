from typing import Dict
import pytest
from app.schemas.user import UserCreate


@pytest.fixture
def user_create_google_dict():
    return {"name": "test_google", "email": "test@gmail.com", "login_method": "google"}


@pytest.fixture
def user_create_password_dict():
    return {
        "name": "test_password",
        "email": "test@test.com",
        "login_method": "password",
        "salt": "salt",
        "hased_password": "hash",
    }


@pytest.fixture
def user_create_google(user_create_google_dict: Dict):
    return UserCreate(**user_create_google_dict)


@pytest.fixture
def user_create_password(user_create_password_dict: Dict):
    return UserCreate(**user_create_password_dict)
