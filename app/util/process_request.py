import jwt
import os
from app.schemas.user import User, UserWithToken
from flask import Request, abort
from datetime import datetime, timedelta, timezone
from flask import Request
from cryptography import x509
from app.config.app_config import conf


PRIVATE_KEY_LOCATION = os.path.join(conf.CERTS_DIR, conf.DOMAIN_NAME, "privkey1.pem")
PUBLIC_CERT_LOCATION = os.path.join(conf.CERTS_DIR, conf.DOMAIN_NAME, "cert1.pem")


def get_public_key():
    with open(PUBLIC_CERT_LOCATION, "rb") as f:
        cert = x509.load_der_x509_certificate(f.read())
    return cert.public_key()


def get_private_key():
    with open(PRIVATE_KEY_LOCATION, "rb") as f:
        key = f.read()
    return key


def encode_token(user: User) -> UserWithToken:
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
    return UserWithToken(**user.dict(), access_token=encoded)


def decode_token(token: str):
    try:
        data = jwt.decode(jwt=token, key=get_public_key, algorithms=["RS256"])
    except:
        abort(401, "Decode token error!")
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


def get_user_info_from_request(request: Request) -> User:
    """
    As the user-management will only issue httpOnly token,
    react frontend cannot get it. and chrome will only add the token
    in the cookie accompanying the request sent to the server.
    """
    token = get_token_from_cookie(request)
    if token is None:
        abort(401, "no token!!!")
    else:
        user = User(**decode_token(token=token))
        return user