# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
import requests
from sqlalchemy.sql.functions import user

# from app.exceptions.casbin_rule import PolicyDoesNotExist, PolicyIsAlreadyThere
from app.exceptions.rbac import NotAuthorized
from app.repo.user import get_user_by_email
from app.schemas.user import (
    LoginMethodEnum,
    UserCreate,
    User,
    UserInResponse,
    UserLoginWithPassword,
    UserRegisterWithPassword,
)
from app.schemas.pagination import QueryPagination
from app.util.response_util import create_response
import app.service.user as userService
from app.util.app_logging import get_logger
from app.util.process_request import get_user_info_from_request, get_google_user_from_request
from app.exceptions.user import UserDoesNotExist, UserEmailAlreadyExist
from flask_wtf import csrf
from app.util.process_request import encode_token
from app.util.password import verify_password

# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("core", __name__, url_prefix="/api")
logger = get_logger(__name__)


@bp.route("/register", methods=["POST"])
@validate()
def password_user_register(body: UserRegisterWithPassword):
    # user = userService.get_user_with_email(email=body.email)
    # if user is not None:
    #     return create_response(
    #         success=False, status_code=409, message="user already exists"
    #     )
    try:
        userService.create_user_with_password(
            name=body.name, email=body.email, password=body.password
        )
    except UserEmailAlreadyExist as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)


@bp.route("/login", methods=["POST"])
@validate()
def login_with_password(body: UserLoginWithPassword):
    # user_login = request.body_params
    user = userService.get_user_with_email(email=body.email)
    if user is None:
        return create_response(
            success=False, status_code=401, message="Email or Password is incorrect"
        )
    if user.login_method != LoginMethodEnum.password:
        return create_response(
            success=False, status_code=400, message="Please login with google"
        )
    if not verify_password(
        password=body.password, salt=user.salt, hashed_password=user.hashed_password
    ):
        return create_response(
            success=False, status_code=401, message="Email or Password is incorrect"
        )
    user_with_token = encode_token(user_in_reponse=UserInResponse(**user.dict()))
    return create_response(
        response=user_with_token,
        cookies={"token": user_with_token.access_token},
    )


@bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    # Have your server decode the id_token
    # by using a common JWT library such as jwt-simple
    # or by sending a GET request to https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=YOUR_TOKEN_HERE
    # if the user is not there, create the user...

    google_user = get_google_user_from_request(reuqest=request)
    # we need to check if the client id matches!
    # create the user!!!
    user = userService.get_user_with_email(email=google_user.email)
    if user is None:
        try:
            userService.create_user_with_google_login(
                name=google_user.name, email=google_user.email
            )
        except UserEmailAlreadyExist as e:
            return create_response(success=False, message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.debug(e, exc_info=True)
            return create_response(success=False, message=str(e), status_code=500)
    else:  # the user exists
        if user.login_method != LoginMethodEnum.google:
            return create_response(success=False, status_code=400, message="please login with email password")
        user_with_token = encode_token(user_in_reponse=UserInResponse(**user.dict()))
        return create_response(
            response=user_with_token,
            cookies={"token": user_with_token.access_token},
        )


@bp.route("/logout", methods=["POST"])
def logout():
    # here is how to do the backend logout
    # while the frontend just wipeout the token

    # there is an iat field in the token
    # when login, iat, user.last_logout is None or t1

    # when authenticating:
    # user management knows user.last_logout
    # if iat > last_logout, allow , else, deny

    # when user logout, update the user.last_logout to t2 (t2 will be > X)
    # now if the user try to use the same token,
    # when authenticating:
    # iat will be < last_logout, then deny

    # this thing is better done with a proper database, so it is not coded here
    # as i want to make this a very light code to show authN/Z
    return create_response(message="you are logged out", cookies_to_delete=["token"])


@bp.route("/authenticate", methods=["POST"])
def authenticate():
    # so here we need to check user.last_logout vs token's iat..
    print(request.headers)
    user = get_user_info_from_request(request=request)

    # try to get the user via email...
    try:
        userService.get_item(item_id=user.id)
        return create_response(status=200, message="welcome")
    except UserDoesNotExist as e:
        return create_response(success=False, message=e.message, status=403)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)


@bp.route("/csrf-token", methods=["GET"])
def get_anti_csrf_token():
    return {"myCsrfToken": csrf.generate_csrf()}


@bp.route("/internal/get_public_key", methods=["GET"])
def get_public_key():
    return ""
