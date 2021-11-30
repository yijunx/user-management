# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.schemas.user import (
    User,
    GoogleUser,
    LoginMethodEnum,
    UserEmailVerificationParam,
    UserForgetPassword,
    UserInLinkVerification,
    UserInResponse,
    UserInResponseWithAdminInfo,
    UserLoginWithPassword,
    UserPasswordResetVerificationParam,
    UserPasswordResetVerificationPayload,
    UserRegisterWithPassword,
)
from app.util.response_util import create_response
import app.service.user as userService
import app.service.rbac as rbacService
from app.util.app_logging import get_logger
from app.util.process_request import (
    decode_token,
    get_user_info_from_request,
    get_google_user_from_request,
    encode_access_token,
)
from app.exceptions.user import (
    UserDoesNotExist,
    UserEmailAlreadyExist,
    UserEmailAlreadyVerified,
    UserPasswordResetNotSame,
    UserPasswordResetSaltNotMatch,
)
from flask_wtf import csrf
from app.util.password import verify_password


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
        user = userService.create_user_with_password(
            name=body.name, email=body.email, password=body.password
        )
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
        message=f"你好! {body.name}, 欢迎👏",
    )


@bp.route("/forget_password", methods=["POST"])
@validate()
def forget_password(body: UserForgetPassword):
    """this function sends user a link to reset password
    in this link, there is a token, no one can fake the token"""
    try:
        userService.send_email_for_password_reset(email=body.email)
    except UserDoesNotExist as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=True, message="密码重置邮件已发送，请点击里面的链接")


@bp.route("/reset_password_verification", methods=["GET"])
@validate()
def reset_password_link_verification(query: UserPasswordResetVerificationParam):
    """the page will check here to verify the password
    this will check this is the user who has the access to the email he claimed
    well this endpoint has no use..."""

    # check if the browser sends the cookie or not
    # if there is cookie
    user_in_link_verification = UserInLinkVerification(
        **decode_token(token=query.token)
    )
    try:
        user = userService.get_user(item_id=user_in_link_verification.id)
    except UserDoesNotExist as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    if user.salt == user_in_link_verification.salt:
        # here user is valid.. then this page can be used
        # now user is there, password is ok, page can be rendered
        # for the user to key in the new password and new password again
        return create_response(success=True)
    return create_response(success=False, status_code=400)


@bp.route("/reset_password_without_login", methods=["POST"])
@validate()
def reset_password_without_login(body: UserPasswordResetVerificationPayload):
    """requires token, and new password, and new password again"""
    if body.token:
        user_in_link_verification = UserInLinkVerification(
            **decode_token(token=body.token)
        )
    else:
        return create_response(success=False, message="no token provided")

    try:
        _ = userService.update_user_password(
            item_id=user_in_link_verification.id,
            new_password=body.new_password,
            new_password_again=body.new_password_again,
            salt=user_in_link_verification.salt,
        )
    except (
        UserDoesNotExist,
        UserPasswordResetSaltNotMatch,
        UserPasswordResetNotSame,
    ) as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=True, message="成功重置密码👏")


@bp.route("/email_verification", methods=["GET"])
@validate()
def verify_email(query: UserEmailVerificationParam):
    user_in_link_verification = UserInLinkVerification(
        **decode_token(token=query.token)
    )
    try:
        user = userService.get_user(item_id=user_in_link_verification.id)
    except UserDoesNotExist as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    if user.email_verified:
        return create_response(success=True, message="成功验证电子邮件地址👏 （但是你已经验证过啦）")
    if user.salt == user_in_link_verification.salt:
        userService.update_user_email_verified(item_id=user.id)
        return create_response(success=True, message="成功验证电子邮件地址👏")
    return create_response(success=False, status_code=400)


@bp.route("/login", methods=["POST"])
@validate()
def login_with_password(body: UserLoginWithPassword):
    # user_login = request.body_params
    user = userService.get_user_with_email(email=body.email)
    if user is None:
        return create_response(success=False, status_code=401, message="密码或者电子邮箱填错了")
    if user.login_method != LoginMethodEnum.password:
        return create_response(success=False, status_code=409, message="请用Google登陆")
    if not verify_password(
        password=body.password, salt=user.salt, hashed_password=user.hashed_password
    ):
        return create_response(success=False, status_code=401, message="密码或者电子邮箱填错啦")
    # if not user.email_verified:
    #     return create_response(
    #         success=False, status_code=406, message="Email not verified"
    #     )

    # here is some notes about if email is verified.
    # user without verified email cannot do anything
    # can just login, and request verification email again
    admin_info = rbacService.admin_check(user_id=user.id)
    userService.update_user_login_time(item_id=user.id)
    user_in_reponse_with_admin_info = UserInResponseWithAdminInfo(
        **user.dict(), admin_info=admin_info
    )
    return create_response(
        response=user_in_reponse_with_admin_info,
        cookies={"token": encode_access_token(user=user)},
    )


@bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    # Have your server decode the id_token
    # by using a common JWT library such as jwt-simple
    # or by sending a GET request to https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=YOUR_TOKEN_HERE
    # if the user is not there, create the user...

    print("login with google request is here..")
    google_user: GoogleUser = get_google_user_from_request(request=request)
    user = userService.get_user_with_email(email=google_user.email)
    if user is None:
        try:
            print("try creating user...")
            user = userService.create_user_with_google_login(
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
    admin_info = rbacService.admin_check(user_id=user.id)
    userService.update_user_login_time(item_id=user.id)
    user_in_reponse_with_admin_info = UserInResponseWithAdminInfo(
        **user.dict(), admin_info=admin_info
    )
    return create_response(
        response=user_in_reponse_with_admin_info,
        cookies={"token": encode_access_token(user=user)},
    )


@bp.route("/logout", methods=["POST"])
def logout():
    user_in_token = get_user_info_from_request(request=request)
    userService.update_user_logout_time(item_id=user_in_token.id)
    return create_response(message="you are logged out", cookies_to_delete=["token"])


@bp.route("/send_email_verification", methods=["POST"])
@validate()
def send_verify_email():
    """this is for user to ask for email verification again,
    this is only for logged in user"""
    user_in_token = get_user_info_from_request(request=request)
    try:
        userService.send_email_verification(user_in_token=user_in_token)
    except (UserDoesNotExist, UserEmailAlreadyVerified) as e:
        return create_response(success=False, message=e.message, status=403)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(status=200, message="verification email sent!!!")


@bp.route("/reset_password_after_login", methods=["POST"])
@validate()
def reset_password_after_login(body: UserPasswordResetVerificationPayload):
    """requires token, and new password, and new password again"""
    user_in_token = get_user_info_from_request(request=request)
    try:
        _ = userService.update_user_password(
            item_id=user_in_token.id,
            new_password=body.new_password,
            new_password_again=body.new_password_again,
        )
    except (
        UserDoesNotExist,
        UserPasswordResetNotSame,
    ) as e:
        return create_response(success=False, message=str(e), status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=True)


@bp.route("/authenticate", methods=["POST"])
def authenticate():
    """this is for all other microservices, must go through here to validate token
    with the public key
    """
    print(request.headers)
    user_in_token = get_user_info_from_request(request=request)
    try:
        user = userService.get_user(item_id=user_in_token.id)

        # check if the user's email is verified
        if user.login_method == LoginMethodEnum.password:
            if not user.email_verified:
                return create_response(
                    status=400,
                    message="you must verify your email before doing any contribution",
                )
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


# @bp.route("/csrf-token", methods=["GET"])
# def get_anti_csrf_token():
#     return {"myCsrfToken": csrf.generate_csrf()}
