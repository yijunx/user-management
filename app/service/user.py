from datetime import datetime, timezone
from app.db.database import get_db
from app.schemas.pagination import QueryPagination
from app.schemas.user import LoginMethodEnum, UserCreate, User, UserWithPaging
from app.schemas.casbin_rule import CasbinPolicy
from app.casbin.role_definition import (
    SpecificResourceRightsEnum,
    SpecificResourceActionsEnum,
    PolicyTypeEnum,
)
from app.service.util import get_resource_id, get_item_id, authorize
from app.util.password import create_hashed_password
from app.config.app_config import conf
import app.repo.user as userRepo


def create_user_with_google_login(name: str, email: str):
    user_create = UserCreate(
        name=name, email=email, login_method=LoginMethodEnum.google
    )
    with get_db() as db:
        userRepo.create(db=db, item_create=user_create)


def create_user_with_password(name: str, email: str, password):
    salt, hashed_password = create_hashed_password(password=password)
    user_create = UserCreate(
        name=name,
        email=email,
        login_method=LoginMethodEnum.password,
        salt=salt,
        hashed_password=hashed_password,
    )
    with get_db() as db:
        userRepo.create(db=db, item_create=user_create)


def list_users(query_pagination: QueryPagination) -> UserWithPaging:
    with get_db() as db:
        db_items, paging = userRepo.get_all(db=db, query_pagination=query_pagination)
        items = [User.from_orm(x) for x in db_items]
    return UserWithPaging(data=items, paging=paging)


# @authorize(action=SpecificResourceActionsEnum.get)
def get_user(item_id: str) -> User:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        item = User.from_orm(db_item)
    return item


def get_user_with_email(email: str) -> User:
    with get_db() as db:
        db_item = userRepo.get_by_email(db=db, email=email)
        item = User.from_orm(db_item)
    return item


# @authorize(action=SpecificResourceActionsEnum.patch)
# def patch_item(item_id: str, user: User, item_patch: ItemPatch) -> Item:
#     with get_db() as db:
#         db_item = itemRepo.patch(
#             db=db, item_id=item_id, user=user, item_patch=item_patch
#         )
#         item = Item.from_orm(db_item)
#     return item


# @authorize(action=SpecificResourceActionsEnum.delete)
# def delete_item(item_id: str, user: User) -> None:
#     with get_db() as db:
#         itemRepo.delete(db=db, item_id=item_id)
#         casbinruleRepo.delete_policies_by_resource_id(
#             db=db,
#             items_user_right=ItemsUserRight(
#                 resource_id=get_resource_id(item_id=item_id)
#             ),
#         )
