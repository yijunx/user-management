from app.util.password import create_hashed_password
from app.schemas.user import UserCreate, LoginMethodEnum, User
from datetime import datetime, timezone
from app.db.database import get_db
import app.repo.user as userRepo
import os

    
def seed_or_get_admin_user() -> str:

    name=os.getenv("ADMIN_USER_NAME")
    email=os.getenv("ADMIN_USER_EMAIL")
    password=os.getenv("ADMIN_USER_PASSWORD")

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
        db_item = userRepo.get_by_email(db=db, email=email)
        if db_item is None:
            db_item = userRepo.create(db=db, item_create=user_create)
        user = User.from_orm(db_item)
    return user.id