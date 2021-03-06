# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.casbin.role_definition import ResourceActionsEnum
from app.exceptions.rbac import NotAuthorized
from app.schemas.pagination import QueryPagination
from app.schemas.user import (
    UserInDecodedToken,
    UserInResponse,
    UserInResponseWithAdminInfo,
    UserPatch,
    UserRegisterWithPassword,
    User,
)
import app.service.user as userService
import app.service.rbac as rbacService
from app.util.app_logging import get_logger
from app.exceptions.user import UserDoesNotExist, UserEmailAlreadyExist
from app.casbin.decorator import authorize_user_domain
from app.util.response_util import create_response

# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("user", __name__, url_prefix="/api/users")
logger = get_logger(__name__)


@bp.route("", methods=["POST"])
@authorize_user_domain(action=ResourceActionsEnum.create_user)
@validate()
def create_password_user(body: UserRegisterWithPassword):
    actor: User = request.environ["actor"]
    print(f"creating {body.name} by {actor.name} ")
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
        message="User registered, pls check email and verify it, pls pls pls",
    )


@bp.route("", methods=["GET"])
@authorize_user_domain(action=ResourceActionsEnum.list_users)
@validate()
def list_users(query: QueryPagination):
    try:
        users_with_paging = userService.list_users(query_pagination=query)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        response=users_with_paging,
    )


@bp.route("/<user_id>", methods=["GET"])
@authorize_user_domain(require_casbin=False)
@validate()
def get_user(user_id: str):
    """doc string here"""
    actor: User = request.environ["actor"]
    try:
        user = userService.get_user_in_response(item_id=user_id, actor=actor)
        admin_info = rbacService.admin_check(user_id=actor.id)
        user_in_reponse_with_admin_info = UserInResponseWithAdminInfo(
            **user.dict(), admin_info=admin_info
        )
    except (UserDoesNotExist, NotAuthorized) as e:
        return create_response(
            success=False, message=e.message, status_code=e.status_code
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=200,
        response=user_in_reponse_with_admin_info,
    )


@bp.route("/<user_id>", methods=["PATCH"])
@authorize_user_domain(require_casbin=False)
@validate()
def patch_user(user_id: str, body: UserPatch):
    actor: User = request.environ["actor"]
    try:
        user = userService.update_user_detail(
            item_id=user_id, user_patch=body, actor=actor
        )

    except (UserDoesNotExist, NotAuthorized) as e:
        return create_response(
            success=False, message=e.message, status_code=e.status_code
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=200,
        response=user,
    )


@bp.route("/<user_id>", methods=["DELETE"])
@authorize_user_domain(action=ResourceActionsEnum.delete_user)
@validate()
def delete_user(user_id: str):
    """this is admin action desu"""
    try:
        userService.delete_user(item_id=user_id)
    except UserDoesNotExist as e:
        return create_response(
            success=False, message=e.message, status_code=e.status_code
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=False, message="user deleted..")


@bp.route("/<user_id>/ban", methods=["POST"])
@authorize_user_domain(action=ResourceActionsEnum.ban_user)
def ban_user(user_id: str):
    try:
        userService.ban_user(item_id=user_id)
    except UserDoesNotExist as e:
        return create_response(
            success=False, message=e.message, status_code=e.status_code
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=False, message="user banned..")


@bp.route("/<user_id>/unban", methods=["POST"])
@authorize_user_domain(action=ResourceActionsEnum.unban_user)
def unban_user(user_id: str):
    try:
        userService.unban_user(item_id=user_id)
    except UserDoesNotExist as e:
        return create_response(
            success=False, message=e.message, status_code=e.status_code
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(success=False, message="user unbanned..")


@bp.route("/<user_id>/roles", methods=["GET"])
@authorize_user_domain(action=ResourceActionsEnum.unban_user)
@validate()
def get_user_roles(user_id: str):
    actor: User = request.environ["actor"]
    print(f"unban user {user_id} by {actor.name}, not implemeted yet")
    pass


@bp.route("/<user_id>/roles", methods=["POST"])
@authorize_user_domain(action=ResourceActionsEnum.unban_user)
@validate()
def add_user_roles(user_id: str):
    actor: User = request.environ["actor"]
    print(f"unban user {user_id} by {actor.name}, not implemeted yet")
    pass


@bp.route("/<user_id>/roles/<role_name>", methods=["DELETE"])
@authorize_user_domain(action=ResourceActionsEnum.unban_user)
@validate()
def remove_user_roles(user_id: str):
    actor: User = request.environ["actor"]
    print(f"unban user {user_id} by {actor.name}, not implemeted yet")
    pass
