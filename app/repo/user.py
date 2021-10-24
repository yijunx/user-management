from typing import List, Tuple, Union
from sqlalchemy.sql.expression import and_, or_
from app.schemas.pagination import QueryPagination, ResponsePagination
from app.db.models import models
from sqlalchemy.orm import Session

# from uuid import uuid4
from app.schemas.user import User, UserCreate
from uuid import uuid4
from datetime import datetime, timezone
from app.repo.util import translate_query_pagination
from app.exceptions.user import UserDoesNotExist
from sqlalchemy.exc import IntegrityError


def create(db: Session, item_create: UserCreate) -> models.User:
    db_item = models.User(
        id=str(uuid4()),  # [let db create the id for us]
        name=item_create.name,
        email=item_create.email,
    )
    db.add(db_item)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise Exception("cannot create user due to integrity error")
    return db_item


def delete_all(db: Session) -> None:
    db.query(models.User).delete()


def delete(db: Session, item_id: str) -> None:
    db_item = db.query(models.User).filter(models.User.id == item_id).first()
    if not db_item:
        raise UserDoesNotExist(user_id=item_id)
    db.delete(db_item)


def get(db: Session, item_id: str) -> models.User:
    db_item = db.query(models.User).filter(models.User.id == item_id).first()
    if not db_item:
        raise UserDoesNotExist(item_id=item_id)
    return db_item


def get_user_by_email(db: Session, email: str) -> Union[models.User, None]:
    db_item = db.query(models.User).filter(models.User.email == email).first()
    return db_item


# def patch(db: Session, item_id: str, item_patch: ItemPatch, user: User) -> models.Item:
#     db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
#     if not db_item:
#         raise ItemDoesNotExist(item_id=item_id)
#     else:
#         db_item.description = item_patch.description
#         # and log the user id, stuff into the db_item,
#         # like last_modified_by, at stuff
#     return db_item


def get_all(
    db: Session, query_pagination: QueryPagination, item_ids: List[str] = None
) -> Tuple[List[models.User], ResponsePagination]:
    # here is admin is decided by the casbin rules in the service level...

    query = db.query(models.User)

    if item_ids is not None:  # cos it could be an empty list!!
        query = query.filter(models.User.id.in_(item_ids))
    if query_pagination.name:
        query = query.filter(
            models.User.name.ilike(f"%{query_pagination.name}%"),
        )

    total = query.count()
    limit, offset, paging = translate_query_pagination(
        query_pagination=query_pagination, total=total
    )

    db_items = query.order_by(models.User.name.desc()).limit(limit).offset(offset).all()
    paging.page_size = len(db_items)
    return db_items, paging
