from app.schemas.user import GoogleUser


def fake_google_user():
    return GoogleUser(name="api_test_google_user", email="api_test_user@google.com")
