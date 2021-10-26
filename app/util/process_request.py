import jwt
import os
from app.schemas.user import (
    GoogleUser,
    UserInDecodedToken,
    UserInResponse,
)
from flask import Request, abort
from datetime import datetime, timedelta, timezone
from flask import Request
from cryptography import x509
from app.config.app_config import conf
import requests


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


def encode_token(user_in_reponse: UserInResponse) -> str:
    additional_token_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=60 * 60 * 8),
        "iat": datetime.now(timezone.utc),
        "iss": conf.DOMAIN_NAME,
    }
    payload = user_in_reponse.dict()
    payload.update(additional_token_payload)
    encoded = jwt.encode(
        payload=payload,
        key=get_private_key(),
        algorithm="RS256",
    )
    return encoded


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


def get_user_info_from_request(request: Request) -> UserInDecodedToken:
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
        user = UserInDecodedToken(**decode_token(token=token))
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
