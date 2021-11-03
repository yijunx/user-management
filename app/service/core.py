from datetime import datetime, timezone
from app.db.database import get_db
from app.schemas.user import LoginMethodEnum, UserCreate, User
from app.util.password import create_hashed_password
import app.repo.user as userRepo
from typing import Union


def create_user_with_google_login(name: str, email: str) -> User:
    user_create = UserCreate(
        name=name, email=email, login_method=LoginMethodEnum.google
    )
    with get_db() as db:
        db_item = userRepo.create(db=db, item_create=user_create)
        user = User.from_orm(db_item)
    return user


def create_user_with_password(name: str, email: str, password) -> User:
    salt, hashed_password = create_hashed_password(password=password)
    user_create = UserCreate(
        name=name,
        email=email,
        created_at=datetime.now(timezone.utc),
        login_method=LoginMethodEnum.password,
        salt=salt,
        hashed_password=hashed_password,
        email_verified=False,
    )
    with get_db() as db:
        db_item = userRepo.create(db=db, item_create=user_create)
        user = User.from_orm(db_item)
    return user


def get_user(item_id: str) -> User:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        item = User.from_orm(db_item)
    return item


def get_user_with_email(email: str) -> Union[User, None]:
    with get_db() as db:
        db_item = userRepo.get_by_email(db=db, email=email)
        item = None if db_item is None else User.from_orm(db_item)
    return item


def update_user_login_time(item_id: str) -> None:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        db_item.last_login = datetime.now(timezone.utc)


def update_user_email_verified(item_id: str) -> None:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        db_item.email_verified = True


def update_user_logout_time(item_id: str) -> None:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        db_item.last_logout = datetime.now(timezone.utc)


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
