# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.casbin.role_definition import ResourceActionsEnum
from app.schemas.pagination import QueryPagination
from app.schemas.user import (
    UserInEmailVerification,
    UserInResponse,
    UserPatch,
    UserRegisterWithPassword,
    User,
)
import app.service.user as userService
from app.util.app_logging import get_logger
from app.exceptions.user import UserDoesNotExist, UserEmailAlreadyExist
from app.casbin.decorator import authorize_user_domain
from app.util.email_handler import send_email_verification
from app.util.response_util import create_response
from app.util.process_request import (
    encode_email_verification_token,
)
# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("user", __name__, url_prefix="/api/users")
logger = get_logger(__name__)


@bp.route("/", methods=['POST'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.create_user)
def create_password_user(body: UserRegisterWithPassword, actor: User):
    print(f"creating {body.name} by {actor.name} ")
    try:
        user = userService.create_user_with_password(
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




@bp.route("/", methods=['GET'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.list_users)
def list_users(query: QueryPagination, actor: User):
    try:
        users_with_paging = userService.list_users(
            query_pagination=query
        )
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=201,
        response=users_with_paging,
    )



@bp.route("/<user_id>", methods=['GET'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.get_detail)
def get_user(user_id: str, actor: User):
    try:
        user = userService.get_user_in_response(item_id=user_id)
    except UserDoesNotExist as e:
        return create_response(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=200,
        response=user,
    )



@bp.route("/<user_id>", methods=['PATCH'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.patch_detail)
def patch_user(user_id: str, body: UserPatch, actor: User):
    try:
        user = userService.update_user_detail(item_id=user_id, user_patch=body)
    except UserDoesNotExist as e:
        return create_response(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.debug(e, exc_info=True)
        return create_response(success=False, message=str(e), status_code=500)
    return create_response(
        success=True,
        status_code=200,
        response=user,
    )



@bp.route("/<user_id>", methods=['DELETE'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.delete)
def delete_user(user_id: str, actor: User):
    print(f"deleting user {user_id} by {actor.name}, not implemeted yet")
    return create_response(
        success=False,
        message="not implemented"
    )



@bp.route("/<user_id>/ban", methods=['POST'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.ban_user)
def ban_user(user_id: str, actor: User):
    print(f"ban user {user_id} by {actor.name}, not implemeted yet")
    pass



@bp.route("/<user_id>/unban", methods=['POST'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.unban_user)
def unban_user(user_id: str, actor: User):
    print(f"unban user {user_id} by {actor.name}, not implemeted yet")
    pass



