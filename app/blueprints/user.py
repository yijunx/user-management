# this is for login logout authentication
from flask import Blueprint, request
from flask_pydantic import validate
from app.casbin.role_definition import ResourceActionsEnum
from app.schemas.pagination import QueryPagination
from app.schemas.user import (
    GoogleUser,
    LoginMethodEnum,
    UserCreate,
    UserEmailVerificationParam,
    UserInEmailVerification,
    UserInResponse,
    UserLoginWithPassword,
    UserPatch,
    UserRegisterWithPassword,
    User,
)
from app.util.email_handler import send_email_verification
from app.util.response_util import create_response
import app.service.core as coreService
from app.util.app_logging import get_logger
from app.exceptions.user import UserDoesNotExist, UserEmailAlreadyExist
from app.casbin.decorator import authorize_user_domain
# from app.exceptions.item import ItemDoesNotExist, ItemNameIsAlreadyThere


bp = Blueprint("user", __name__, url_prefix="/api/users")
logger = get_logger(__name__)


@bp.route("/", methods=['POST'])
@validate()
@authorize_user_domain(action=ResourceActionsEnum.create_user)
def create_password_user(body: UserRegisterWithPassword, user: User):
    print("creating user")
    pass




@bp.route("/", methods=['GET'])
@validate()
def list_users(query=QueryPagination):
    pass



@bp.route("/<user_id>", methods=['GET'])
@validate()
def get_user(user_id: str):
    pass



@bp.route("/<user_id>", methods=['PATCH'])
@validate()
def patch_user(user_id: str, body: UserPatch):
    pass



@bp.route("/<user_id>", methods=['DELETE'])
@validate()
def delete_user(user_id: str):
    pass




@bp.route("/<user_id>/ban", methods=['POST'])
@validate()
def ban_user(user_id: str):
    pass



@bp.route("/<user_id>/unban", methods=['POST'])
@validate()
def unban_user(user_id: str):
    pass



