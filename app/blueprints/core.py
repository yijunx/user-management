# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
import requests
# from app.exceptions.casbin_rule import PolicyDoesNotExist, PolicyIsAlreadyThere
from app.exceptions.rbac import NotAuthorized
from app.schemas.user import UserCreate, User
from app.schemas.pagination import QueryPagination
from app.util.response_util import create_response
import app.service.user as userService
from app.util.app_logging import get_logger
from app.util.process_request import get_user_info_from_request
from app.exceptions.user import UserDoesNotExist
from flask_wtf import csrf
from app.util.process_request import encode_token
# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("core", __name__, url_prefix="/api")
logger = get_logger(__name__)


@bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    # Have your server decode the id_token
    # by using a common JWT library such as jwt-simple
    # or by sending a GET request to https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=YOUR_TOKEN_HERE
    # if the user is not there, create the user...
    auth_header: str = request.headers.get("Authorization", None)
    if auth_header is None:
        return create_response(success=False, status_code=401, message="no id token from google")
    id_token = auth_header.split(" ")[1]
    r = requests.get(
        url="https://www.googleapis.com/oauth2/v3/tokeninfo",
        params={"id_token": id_token}
    )
    # create the user from the response
    print(r.json())
    # we need to check if the client id matches!
    # create the user!!!
    item_create = UserCreate(**r.json())

    # now add the user into user db if the user does not exist
    user = userService.create_item(item_create=item_create)  # if the user is there it is ok

    # now user is logged in, need to response with the set-token header
    user_with_token = encode_token(user=user)
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


