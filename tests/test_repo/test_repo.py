import pytest
import app.repo.user as userRepo
from app.schemas.pagination import QueryPagination
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from app.exceptions.user import UserEmailAlreadyExist, UserDoesNotExist


GOOGLE_USER_ID = ""
PASSWORD_USER_ID = ""


def test_create_google_user(db: Session, user_create_google: UserCreate):
    db_item = userRepo.create(db=db, item_create=user_create_google)
    global GOOGLE_USER_ID
    GOOGLE_USER_ID = db_item.id
    assert db_item.name == user_create_google.name


def test_create_password_user(db: Session, user_create_password: UserCreate):
    db_item = userRepo.create(db=db, item_create=user_create_password)
    global PASSWORD_USER_ID
    PASSWORD_USER_ID = db_item.id
    assert db_item.name == user_create_password.name


def test_create_password_user_again(db: Session, user_create_password: UserCreate):
    with pytest.raises(UserEmailAlreadyExist):
        userRepo.create(db=db, item_create=user_create_password)


def test_get_google_user_by_id(db: Session, user_create_google: UserCreate):
    db_item = userRepo.get(db=db, item_id=GOOGLE_USER_ID)
    assert db_item.email == user_create_google.email


def test_get_password_user_by_name(db: Session, user_create_password: UserCreate):
    db_item = userRepo.get_by_email(db=db, email=user_create_password.email)
    assert db_item.id == PASSWORD_USER_ID


def test_cannot_get_user_by_wrong_id(db: Session):
    with pytest.raises(UserDoesNotExist):
        userRepo.get(db=db, item_id="wrong id")


def test_list_items(db: Session):
    db_items, paging = userRepo.get_all(
        db=db,
        item_ids=[GOOGLE_USER_ID, PASSWORD_USER_ID],
        query_pagination=QueryPagination(),
    )
    ids = [x.id for x in db_items]
    assert GOOGLE_USER_ID in ids
    assert PASSWORD_USER_ID in ids
    assert paging.page_size == 2


def test_delete_item(db: Session):
    userRepo.delete(db=db, item_id=GOOGLE_USER_ID)
    userRepo.delete(db=db, item_id=PASSWORD_USER_ID)


def test_delete_item_again(db: Session):
    with pytest.raises(UserDoesNotExist):
        userRepo.delete(db=db, item_id=GOOGLE_USER_ID)
