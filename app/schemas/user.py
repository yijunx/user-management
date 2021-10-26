from datetime import datetime
from pydantic import BaseModel
from app.casbin.role_definition import SpecificResourceRightsEnum
from typing import List, Optional
from enum import Enum
from app.schemas.pagination import ResponsePagination


class LoginMethodEnum(str, Enum):
    password = "password"
    google = "google"
    # wechat = "wechat"


class UserLoginWithPassword(BaseModel):
    email: str
    password: str


class UserRegisterWithPassword(BaseModel):
    name: str
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: str
    login_method: LoginMethodEnum
    salt: Optional[str]
    hashed_password: Optional[str]


class User(UserCreate):
    id: str
    last_login: datetime
    last_logout: datetime
    email_verified: bool


class UserInResponse(BaseModel):
    """this is the token payload"""

    id: str
    name: str
    login_method: LoginMethodEnum


class UserInDecodedToken(UserInResponse):
    exp: datetime
    iat: datetime
    iss: str


class UserPatch(BaseModel):
    name: Optional[str]
    password: Optional[str]


class UserWithToken(User):
    access_token: str


class UserWithPaging(BaseModel):
    data: List[UserInResponse]
    paging: ResponsePagination


class GoogleUser(BaseModel):
    name: str
    email: str
    picture: str
