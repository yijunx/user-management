from pydantic import BaseModel
from app.casbin.role_definition import SpecificResourceRightsEnum
from typing import List, Optional

from app.schemas.pagination import ResponsePagination


class UserCreate(BaseModel):
    name: str
    email: Optional[str]


class User(UserCreate):
    id: str


class UserWithToken(User):
    access_token: str


class UserWithPaging(BaseModel):
    data: List[User]
    paging: ResponsePagination
