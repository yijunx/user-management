from datetime import datetime, timezone
from app.db.database import get_db
from app.schemas.pagination import QueryPagination
from app.schemas.user import (
    LoginMethodEnum,
    UserCreate,
    User,
    UserInResponse,
    UserWithPaging,
)
from app.schemas.casbin_rule import CasbinPolicy
from app.casbin.role_definition import (
    SpecificResourceRightsEnum,
    SpecificResourceActionsEnum,
    PolicyTypeEnum,
)
from app.service.util import get_resource_id, get_item_id, authorize
from app.util.password import create_hashed_password
import app.repo.user as userRepo
from typing import Union


def list_users(query_pagination: QueryPagination) -> UserWithPaging:
    with get_db() as db:
        db_items, paging = userRepo.get_all(db=db, query_pagination=query_pagination)
        items = [UserInResponse.from_orm(x) for x in db_items]
    return UserWithPaging(data=items, paging=paging)
