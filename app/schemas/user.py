from pydantic import BaseModel
from app.casbin.role_definition import SpecificResourceRightsEnum
from typing import List, Optional

from app.schemas.pagination import ResponsePagination


class User(BaseModel):
    id: str
    name: str
    email: Optional[str]


class UserWithPaging(BaseModel):
    data: List[User]
    paging: ResponsePagination


