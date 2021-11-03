# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.schemas.user import (
    GoogleUser,
    LoginMethodEnum,
    UserEmailVerificationParam,
    UserInEmailVerification,
    UserInResponse,
    UserLoginWithPassword,
    UserRegisterWithPassword,
)
from app.util.email_handler import send_email_verification
from app.util.response_util import create_response
import app.service.core as coreService
from app.util.app_logging import get_logger
from app.util.process_request import (
    decode_token,
    get_user_info_from_request,
    get_google_user_from_request,
    encode_access_token,
    encode_email_verification_token,
)
from app.exceptions.user import UserDoesNotExist, UserEmailAlreadyExist
from flask_wtf import csrf
from app.util.password import verify_password

# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("core", __name__, url_prefix="/api")
logger = get_logger(__name__)


@bp.route("/register", methods=["POST"])
@validate()
def password_user_register(body: UserRegisterWithPassword):
    """
    register user email and password login info.
    However this is not the correct way..

    the correct way..
    POST register -> created a line in db with email_verified -> False
    and user cannot login yet, and the account will be deleted in 7 days

    then, use the sendgrip api to send a link to the email
    the link is got GET /api/verify_email?some_info_here=<user_in_response.dict() | encode_with_privatekey>
    user clicks the link in the email
    the backend will receive the request, then decode the token,
    check the email in the jwt is same as the one in db
    and the user can login
    """
    try:
        user = coreService.create_user_with_password(
            name=body.name, email=body.email, password=body.password
        )
        # now send the email
        token = encode_email_verification_token(
            user_in_email_verification=UserInEmailVerification(**user.dict())
        )
        send_email_verification(token=token, user_email=user.email, user_name=user.name)
        user_in_response = UserInResponse(**user.dict())
    except UserEmailAlreadyExist as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=201,
        response=user_in_response,
        message="User registered, pls check email and verify it, pls pls pls",
    )


@bp.route("/email_verification", methods=["GET"])
@validate()
def verify_email(query: UserEmailVerificationParam):
    user_in_email_verification = UserInEmailVerification(
        **decode_token(token=query.token)
    )
    user = coreService.get_user(item_id=user_in_email_verification.id)
    if user.email_verified:
        return create_response(success=True)
    if user.salt == user_in_email_verification.salt:
        coreService.update_user_email_verified(item_id=user.id)
        return create_response(success=True)
    return create_response(success=False, status_code=400)


@bp.route("/login", methods=["POST"])
@validate()
def login_with_password(body: UserLoginWithPassword):
    # user_login = request.body_params
    user = coreService.get_user_with_email(email=body.email)
    if user is None:
        return create_response(
            success=False, status_code=401, message="Email or Password is incorrect"
        )
    if user.login_method != LoginMethodEnum.password:
        return create_response(
            success=False, status_code=409, message="Please login with google"
        )
    if not verify_password(
        password=body.password, salt=user.salt, hashed_password=user.hashed_password
    ):
        return create_response(
            success=False, status_code=401, message="Email or Password is incorrect"
        )
    # if not user.email_verified:
    #     return create_response(
    #         success=False, status_code=406, message="Email not verified"
    #     )

    # here is some notes about if email is verified.
    # user without verified email cannot do anything
    # can just login, and request verification email again

    coreService.update_user_login_time(item_id=user.id)
    user_in_reponse = UserInResponse(**user.dict())
    access_token = encode_access_token(user_in_reponse=user_in_reponse)
    return create_response(
        response=user_in_reponse,
        cookies={"token": access_token},
    )


@bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    # Have your server decode the id_token
    # by using a common JWT library such as jwt-simple
    # or by sending a GET request to https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=YOUR_TOKEN_HERE
    # if the user is not there, create the user...

    print("login with google request is here..")
    google_user: GoogleUser = get_google_user_from_request(request=request)
    user = coreService.get_user_with_email(email=google_user.email)
    if user is None:
        try:
            print("try creating user...")
            user = coreService.create_user_with_google_login(
                name=google_user.name, email=google_user.email
            )
        except UserEmailAlreadyExist as e:
            # well suddenly email is used... there might be such instances..
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
    coreService.update_user_login_time(item_id=user.id)
    user_in_reponse = UserInResponse(**user.dict())
    access_token = encode_access_token(user_in_reponse=user_in_reponse)
    return create_response(
        response=user_in_reponse,
        cookies={"token": access_token},
    )


@bp.route("/logout", methods=["POST"])
def logout():
    user_in_token = get_user_info_from_request(request=request)
    coreService.update_user_logout_time(item_id=user_in_token.id)
    return create_response(message="you are logged out", cookies_to_delete=["token"])


@bp.route("/authenticate", methods=["POST"])
def authenticate():
    # so here we need to check user.last_logout vs token's iat..
    print(request.headers)
    user_in_token = get_user_info_from_request(request=request)
    try:
        user = coreService.get_user(item_id=user_in_token.id)
        if user.last_logout is None or user_in_token.iat > user.last_logout:
            return create_response(status=200, message="welcome")
        else:
            return create_response(
                status=403, message="You have been logged out, pls login again"
            )
    except UserDoesNotExist as e:
        return create_response(success=False, message=e.message, status=403)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)


@bp.route("/csrf-token", methods=["GET"])
def get_anti_csrf_token():
    return {"myCsrfToken": csrf.generate_csrf()}
