from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger
from .base import Base


class User(Base):
    __tablename__ = "users"
    # need to check again after login with wechat is done
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    last_logout = Column(DateTime, nullable=True)


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
