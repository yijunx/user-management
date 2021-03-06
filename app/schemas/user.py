from datetime import datetime, timezone
from pydantic import BaseModel
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


class UserForgetPassword(BaseModel):
    email: str


class UserCreate(BaseModel):
    name: str
    email: str
    created_at: datetime = datetime.now(timezone.utc)
    login_method: LoginMethodEnum
    salt: Optional[str]
    hashed_password: Optional[str]
    email_verified: Optional[bool]


class User(UserCreate):
    id: str
    last_login: Optional[datetime]
    last_logout: Optional[datetime]

    banned: bool

    class Config:
        orm_mode = True


class UserInResponse(BaseModel):
    id: str
    name: str
    email_verified: Optional[bool]
    login_method: LoginMethodEnum


class UserInResponseWithAdminInfo(UserInResponse):
    admin_info: dict


class UserInDecodedToken(UserInResponse):
    exp: datetime
    iat: datetime
    iss: str


class UserPatch(BaseModel):
    """use for users to update name and else, those not sentive stuff"""

    name: Optional[str]
    # password: Optional[str]


class UserWithPaging(BaseModel):
    data: List[UserInResponse]
    paging: ResponsePagination


class GoogleUser(BaseModel):
    name: str
    email: str
    picture: Optional[str]


class UserEmailVerificationParam(BaseModel):
    token: str


class UserPasswordResetVerificationParam(BaseModel):
    token: str


class UserPasswordResetVerificationPayload(BaseModel):
    token: Optional[str]
    new_password: str
    new_password_again: str


class UserInLinkVerification(UserInResponse):
    """here salt is added to make sure the no false link
    when backend check the token in email verification
    will check if the salt is same as user's salt"""

    salt: str
