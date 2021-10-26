# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.schemas.user import (
    LoginMethodEnum,
    UserInResponse,
    UserLoginWithPassword,
    UserRegisterWithPassword,
)
from app.util.response_util import create_response
import app.service.user as userService
from app.util.app_logging import get_logger
from app.util.process_request import (
    get_user_info_from_request,
    get_google_user_from_request,
)
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
    userService.update_user_login_time(item_id=user.id)
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
            return create_response(
                success=False, message=str(e), status_code=e.status_code
            )
        except Exception as e:
            logger.debug(e, exc_info=True)
            return create_response(success=False, message=str(e), status_code=500)
    else:  # the user exists
        if user.login_method != LoginMethodEnum.google:
            return create_response(
                success=False,
                status_code=400,
                message="please login with email password",
            )
        
        # now user is good...
        userService.update_user_login_time(item_id=user.id)
        user_with_token = encode_token(user_in_reponse=UserInResponse(**user.dict()))
        return create_response(
            response=user_with_token,
            cookies={"token": user_with_token.access_token},
        )


@bp.route("/logout", methods=["POST"])
def logout():
    user_in_token = get_user_info_from_request(request=request)
    userService.update_user_logout_time(item_id=user_in_token.id)
    return create_response(message="you are logged out", cookies_to_delete=["token"])


@bp.route("/authenticate", methods=["POST"])
def authenticate():
    # so here we need to check user.last_logout vs token's iat..
    print(request.headers)
    user_in_token = get_user_info_from_request(request=request)
    try:
        user = userService.get_user(item_id=user_in_token.id)
        if user_in_token.iat > user.last_logout:
            return create_response(status=200, message="welcome")
        else:
            return create_response(status=403, message="You have been logged out, pls login again")
    except UserDoesNotExist as e:
        return create_response(success=False, message=e.message, status=403)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)


@bp.route("/csrf-token", methods=["GET"])
def get_anti_csrf_token():
    return {"myCsrfToken": csrf.generate_csrf()}

