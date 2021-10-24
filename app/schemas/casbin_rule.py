from pydantic import BaseModel
from typing import Optional
from app.casbin.role_definition import PolicyTypeEnum


class CasbinPolicy(BaseModel):
    ptype: PolicyTypeEnum
    v0: Optional[str]
    v1: Optional[str]
    v2: Optional[str]
    v3: Optional[str]
    v4: Optional[str]
    v5: Optional[str]

    class Config:
        orm_mode = True


class CasbinPolicyPatch(BaseModel):
    ptype: PolicyTypeEnum
    v0: Optional[str]
    v1: Optional[str]
    v2: Optional[str]
