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


def create_item(item_create: UserCreate) -> Item:
    # here it means every body can post
    # here we can add decorator to let only admin user can create item...
    with get_db() as db:
        db_item = itemRepo.create(db=db, item_create=item_create, creator=user)
        item = Item.from_orm(db_item)
        casbin_policy = CasbinPolicy(
            ptype=PolicyTypeEnum.p,
            v0=user.id,
            v1=get_resource_id(item_id=item.id),
            v2=SpecificResourceRightsEnum.own,
            created_at=datetime.now(timezone.utc),
            created_by=user.id,
        )
        casbinruleRepo.create(db=db, casbin_policy=casbin_policy)
    return item


def list_items(query_pagination: QueryPagination, user: User) -> ItemWithPaging:
    with get_db() as db:
        if not user.is_admin:
            policies, _ = casbinruleRepo.get_all_policies_given_user(
                db=db,
                users_item_right=UsersItemRight(user_id=user.id),
                query_pagination=QueryPagination(size=-1),
                resource_name=conf.RESOURCE_NAME,
                is_admin=False,
            )
            item_ids = [get_item_id(resource_id=p.v1) for p in policies]
            db_items, paging = itemRepo.get_all(
                db=db, query_pagination=query_pagination, item_ids=item_ids
            )
        else:
            db_items, paging = itemRepo.get_all(
                db=db, query_pagination=query_pagination
            )
        items = [Item.from_orm(x) for x in db_items]
    return ItemWithPaging(data=items, paging=paging)


@authorize(action=SpecificResourceActionsEnum.get)
def get_item(item_id: str, user: User) -> Item:
    with get_db() as db:
        db_item = itemRepo.get(db=db, item_id=item_id)
        item = Item.from_orm(db_item)
    return item


@authorize(action=SpecificResourceActionsEnum.patch)
def patch_item(item_id: str, user: User, item_patch: ItemPatch) -> Item:
    with get_db() as db:
        db_item = itemRepo.patch(
            db=db, item_id=item_id, user=user, item_patch=item_patch
        )
        item = Item.from_orm(db_item)
    return item


@authorize(action=SpecificResourceActionsEnum.delete)
def delete_item(item_id: str, user: User) -> None:
    with get_db() as db:
        itemRepo.delete(db=db, item_id=item_id)
        casbinruleRepo.delete_policies_by_resource_id(
            db=db,
            items_user_right=ItemsUserRight(
                resource_id=get_resource_id(item_id=item_id)
            ),
        )


@authorize(action=SpecificResourceActionsEnum.share)
def share_item(item_id: str, user: User, user_share: UserShare) -> None:
    # first need to send user_share to user management to check
    # if this user exists
    # but never mind, we just add it here
    with get_db() as db:
        casbin_policy = CasbinPolicy(
            ptype=PolicyTypeEnum.p,
            v0=user_share.user_id,
            v1=get_resource_id(item_id=item_id),
            v2=user_share.right,
            created_at=datetime.now(timezone.utc),
            created_by=user.id,
        )
        # there will be error raised in create if duplicated
        casbinruleRepo.create(db=db, casbin_policy=casbin_policy)


@authorize(action=SpecificResourceActionsEnum.share)
def patch_user_rights_of_an_item(
    item_id: str, user: User, user_share: UserShare
) -> None:
    with get_db() as db:
        casbinruleRepo.update_specific_policy(
            db=db,
            resource_id=get_resource_id(item_id=item_id),
            user_id=user_share.user_id,
            right_to_update=user_share.right,
        )


@authorize(action=SpecificResourceActionsEnum.unshare)
def unshare_item(item_id: str, user: User, sharee_id: str) -> None:
    with get_db() as db:
        casbinruleRepo.delete_specific_policy(
            db=db, user_id=sharee_id, resource_id=get_resource_id(item_id=item_id)
        )


@authorize(action=SpecificResourceActionsEnum.get)
def list_items_user_rights(
    item_id: str, user: User, query_pagination: QueryPagination
) -> UsersItemRightWithPaging:
    """show who has what right on a given item"""
    with get_db() as db:
        policies, paging = casbinruleRepo.get_all_policies_given_item(
            db=db,
            items_user_right=ItemsUserRight(
                resource_id=get_resource_id(item_id=item_id)
            ),
            query_pagination=query_pagination,
        )
        users_item_rights = [UsersItemRight(user_id=p.v0, right=p.v2) for p in policies]
        # if there is user table then need to take the user id
        # to get full info from the user table
    return UsersItemRightWithPaging(data=users_item_rights, paging=paging)


@authorize(admin_required=True)
def admin_only_action(item_id: str, user: User):
    # this is only for admin
    return {"hello": item_id, "i am": user.id}


def clean_up() -> None:
    with get_db() as db:
        itemRepo.delete_all(db=db)
