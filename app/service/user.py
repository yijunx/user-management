from datetime import datetime, timezone
from app.casbin.resource_id_converter import get_resource_id_from_user_id
from app.casbin.role_definition import ResourceRightsEnum
from app.db.database import get_db
from app.exceptions.user import UserEmailAlreadyVerified
from app.schemas.pagination import QueryPagination
from app.schemas.user import (
    LoginMethodEnum,
    UserCreate,
    User,
    UserInDecodedToken,
    UserInLinkVerification,
    UserInResponse,
    UserPatch,
    UserWithPaging,
)
from app.util.password import create_hashed_password
import app.repo.user as userRepo
from typing import Union
from app.casbin.enforcer import casbin_enforcer
from app.util.async_worker import celery, CeleryTaskEnum
from app.util.process_request import encode_email_verification_token
from app.config.app_config import conf


def create_user_with_google_login(name: str, email: str) -> User:
    user_create = UserCreate(
        name=name, email=email, login_method=LoginMethodEnum.google
    )
    with get_db() as db:
        db_item = userRepo.create(db=db, item_create=user_create)
        user = User.from_orm(db_item)
        # casbinRepo.create_policy(
        #     db=db,
        #     user_id=user.id,
        #     resource_id=get_resource_id_from_user_id(user.id),
        #     resource_right=ResourceRightsEnum.own,
        # )

        casbin_enforcer.add_policy(
            user.id,
            get_resource_id_from_user_id(user.id),
            ResourceRightsEnum.own,
        )
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
        # this user himself is the owner of himself
        casbin_enforcer.add_policy(
            user.id,
            get_resource_id_from_user_id(user.id),
            ResourceRightsEnum.own,
        )
        token = encode_email_verification_token(
            user_in_email_verification=UserInLinkVerification(**user.dict())
        )
        celery.send_task(
            name=f"{conf.CELERY_SERVICE_NAME}.{CeleryTaskEnum.email_confirmation}",
            kwargs={"token": token, "user_name": user.name, "user_email": user.email},
            queue=conf.CELERY_QUEUE,
        )

    return user


def send_email_verification(user_in_token: UserInDecodedToken) -> None:
    with get_db() as db:
        db_user = userRepo.get(db=db, item_id=user_in_token.id)
        if db_user.login_method == LoginMethodEnum.google or db_user.email_verified:
            raise UserEmailAlreadyVerified()
        user = User.from_orm(db_user)
        token = encode_email_verification_token(
            user_in_email_verification=UserInLinkVerification(**user.dict())
        )
        celery.send_task(
            name=f"{conf.CELERY_SERVICE_NAME}.{CeleryTaskEnum.email_confirmation}",
            kwargs={
                "token": token,
                "user_name": user.name,
                "user_email": user.email,
            },
            queue=conf.CELERY_QUEUE,
        )


def list_users(query_pagination: QueryPagination) -> UserWithPaging:
    with get_db() as db:
        db_items, paging = userRepo.get_all(db=db, query_pagination=query_pagination)
        items = [
            UserInResponse(id=x.id, name=x.name, login_method=x.login_method)
            for x in db_items
        ]
    return UserWithPaging(data=items, paging=paging)


def get_user(item_id: str) -> User:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        item = User.from_orm(db_item)
    return item


def get_user_in_response(item_id: str) -> UserInResponse:
    with get_db() as db:
        db_item = userRepo.get(db=db, item_id=item_id)
        item = User.from_orm(db_item)
    return UserInResponse(**item.dict())


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


def update_user_detail(item_id: str, user_patch: UserPatch) -> UserInResponse:
    with get_db() as db:
        db_item = userRepo.patch(db=db, item_id=item_id, item_patch=user_patch)
        item = User.from_orm(db_item)
    return UserInResponse(**item.dict())


def update_user_password() -> None:
    return


def unregister_user(item_id: str) -> None:
    """this is from user, not admin.."""

    # remember to update the casbin rules
    pass


def delete_user(item_id: str) -> None:
    """well this is really delete, only admin can do this"""
    with get_db() as db:
        userRepo.delete(db=db, item_id=item_id)
        # the below step should be down via db...
        casbin_enforcer.remove_policy(
            item_id, get_resource_id_from_user_id(item_id), ResourceRightsEnum.own
        )
        # casbinRepo.delete_policies_by_resource_id(
        #     db=db, resource_id=get_resource_id_from_user_id(item_id)
        # )
