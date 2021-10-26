from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger, Boolean
from .base import Base


class User(Base):
    __tablename__ = "users"
    # need to check again after login with wechat is done
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    # login method is password or google
    login_method = Column(String, nullable=False)

    # timing info
    last_login = Column(DateTime, nullable=False)
    last_logout = Column(DateTime, nullable=True)

    # password info for those login with password
    salt = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    email_verified = Column(Boolean, nullable=True)


class CasbinRule(Base):
    __tablename__ = "casbin_rule"
    __table_args__ = (UniqueConstraint("v0", "v1", name="_v0_v1_uc"),)
    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    ptype = Column(String, nullable=False)
    v0 = Column(String, nullable=True)
    v1 = Column(String, nullable=True)
    v2 = Column(String, nullable=True)
    v3 = Column(String, nullable=True)
    v4 = Column(String, nullable=True)
    v5 = Column(String, nullable=True)
