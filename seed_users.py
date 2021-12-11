import app.repo.user as UserRepo
from app.db.database import get_db
from app.schemas.user import LoginMethodEnum, UserCreate
from app.util.password import create_hashed_password


def add_initial_users():

    salt, hashed_password = create_hashed_password(password="lyra")
    item_create = UserCreate(
        name="el psy kongroo",
        email="first-user@dialects.io",
        login_method=LoginMethodEnum.google,
        salt=salt,
        hashed_password=hashed_password,
        email_verified=True,
    )
    with get_db() as db:
        first_user = UserRepo.get_by_email(db=db, email=item_create.email)
        if first_user is None:
            UserRepo.create(db=db, item_create=item_create, item_id="first-user-id")


if __name__ == "__main__":
    add_initial_users()
