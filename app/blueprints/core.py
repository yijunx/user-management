# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
# from app.exceptions.casbin_rule import PolicyDoesNotExist, PolicyIsAlreadyThere
from app.exceptions.rbac import NotAuthorized
from app.schemas.user import UserCreate, User
from app.schemas.pagination import QueryPagination
from app.util.response_util import create_response
import app.service.user as userService
from app.util.app_logging import get_logger
from app.util.process_request import get_user_info_from_request
from flask_wtf import csrf
# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("core", __name__, url_prefix="/api")
logger = get_logger(__name__)


@bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    # well there might be login with wechat all sorts of things..
    # valid the token
    # then login...
    
    pass


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
    for u in users:
        if u.email == user.email:
            roles = ",".join([r.name for r in u.roles])
            # so here we need to check user.last_logout vs token's iat..
            # if iat < last logout, deny the access
            return create_response(headers={"X-Roles": roles})
    return create_response(success=False, message="not a good user..", status=403)


@bp.route("/csrf-token", methods=["GET"])
def get_anti_csrf_token():
    return {"myCsrfToken": csrf.generate_csrf()}


@bp.route("/internal/get_public_key", methods=["GET"])
def get_public_key():
    return ""


