from typing import Any, Dict
import jwt
import os
from app.schemas.user import (
    GoogleUser,
    UserInDecodedToken,
    UserInEmailVerification,
    User,
)
from flask import Request, abort
from datetime import datetime, timedelta, timezone
from flask import Request
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.config.app_config import conf
import requests


PRIVATE_KEY_LOCATION = os.path.join(conf.CERTS_DIR, conf.DOMAIN_NAME, "privkey1.pem")
PUBLIC_CERT_LOCATION = os.path.join(conf.CERTS_DIR, conf.DOMAIN_NAME, "cert1.pem")


def get_public_key():
    with open(PUBLIC_CERT_LOCATION, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read(), backend=default_backend())
        key = cert.public_key()
    return key


def get_private_key():
    with open(PRIVATE_KEY_LOCATION, "rb") as f:
        key = f.read()
    return key


def encode_email_verification_token(
    user_in_email_verification: UserInEmailVerification,
) -> str:
    additional_token_payload = {
        # "exp": datetime.now(timezone.utc) + timedelta(seconds=60 * 60 * 48),
        "iat": datetime.now(timezone.utc),
        "iss": conf.DOMAIN_NAME,
    }
    payload = user_in_email_verification.dict()
    payload.update(additional_token_payload)
    encoded = jwt.encode(
        payload=payload,
        key=get_private_key(),
        algorithm="RS256",
    )
    return encoded


def encode_access_token(user: User) -> str:
    additional_token_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=60 * 60 * 8),
        "iat": datetime.now(timezone.utc),
        "iss": conf.DOMAIN_NAME,
    }
    payload = user.dict()
    payload.update(additional_token_payload)
    encoded = jwt.encode(
        payload=payload,
        key=get_private_key(),
        algorithm="RS256",
    )
    return encoded


def decode_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    try:
        data = jwt.decode(
            jwt=token,
            key=get_public_key(),
            algorithms=["RS256"],
            options={"verify_exp": verify_exp},
        )
    except Exception as e:
        print("Error in decoding token")
        print(str(e))
        abort(401, "Cannot decode token!")
    return data


def get_token_from_cookie(request: Request) -> str:
    token: str = request.cookies.get("token", None)
    return token


def get_token_from_authorization_header(request: Request) -> str:
    bearer_auth: str = request.headers.get("Authorization", None)
    if bearer_auth is None:
        return None
    token = bearer_auth.split(" ")[1]
    return token


def get_user_info_from_request(
    request: Request, verify_exp: bool = True
) -> UserInDecodedToken:
    """
    As the user-management will only issue httpOnly token,
    react frontend cannot get it. and chrome will only add the token
    in the cookie accompanying the request sent to the server.
    This is for anthenticate endpoint
    """
    token = get_token_from_cookie(request)
    if token is None:
        abort(401, "no token!!!")
    else:
        user = UserInDecodedToken(**decode_token(token=token, verify_exp=verify_exp))
        return user


def get_google_user_from_request(request: Request) -> GoogleUser:
    """used when ends sends request here after user logined in with google
    Here we need to verify with google if the id_token is valid
    """
    auth_header: str = request.headers.get("Authorization", None)
    if auth_header is None:
        abort(401, "no id token!!!")
    id_token = auth_header.split(" ")[1]
    r = requests.get(
        url="https://www.googleapis.com/oauth2/v3/tokeninfo",
        params={"id_token": id_token},
    )
    r.raise_for_status()
    return GoogleUser(**r.json())
