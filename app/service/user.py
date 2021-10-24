from datetime import datetime, timezone
from app.db.database import get_db
from app.schemas.pagination import QueryPagination
from app.schemas.user import UserCreate, User, UserWithPaging
from app.schemas.casbin_rule import CasbinPolicy
from app.casbin.role_definition import (
    SpecificResourceRightsEnum,
    SpecificResourceActionsEnum,
    PolicyTypeEnum,
)
from app.service.util import get_resource_id, get_item_id, authorize
from app.config.app_config import conf
import app.repo.user as userRepo


def create_item(item_create: UserCreate) -> User:
    # here it means every body can post
    # here we can add decorator to let only admin user can create item...
    with get_db() as db:
        db_item = userRepo.create(db=db, item_create=item_create)
        item = User.from_orm(db_item)
        # well we need to think about casbin rule later...
        # casbin_policy = CasbinPolicy(
        #     ptype=PolicyTypeEnum.p,
        #     v0=user.id,
        #     v1=get_resource_id(item_id=item.id),
        #     v2=SpecificResourceRightsEnum.own,
        #     created_at=datetime.now(timezone.utc),
        #     created_by=user.id,
        # )
        # casbinruleRepo.create(db=db, casbin_policy=casbin_policy)
    return item


def list_items(query_pagination: QueryPagination) -> UserWithPaging:
    with get_db() as db:
        db_items, paging = userRepo.get_all(
            db=db, query_pagination=query_pagination
        )
        items = [User.from_orm(x) for x in db_items]
    return UserWithPaging(data=items, paging=paging)


# @authorize(action=SpecificResourceActionsEnum.get)
def get_item(item_id: str) -> User:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
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
