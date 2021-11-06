from sqlalchemy.sql.expression import and_
from app.db.models import models
from sqlalchemy.orm import Session
from app.schemas.casbin_rule import CasbinPolicy, PolicyTypeEnum
from sqlalchemy.exc import IntegrityError
from app.exceptions.casbin_rule import PolicyIsAlreadyThere


def create(db: Session, casbin_policy: CasbinPolicy) -> models.CasbinRule:
    """Create both g type and p type here"""
    db_item = models.CasbinRule(
        ptype=casbin_policy.ptype,
        v0=casbin_policy.v0,
        v1=casbin_policy.v1,
        v2=casbin_policy.v2,
        v3=casbin_policy.v3,
        v4=casbin_policy.v4,
        v5=casbin_policy.v5,
    )
    db.add(db_item)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise PolicyIsAlreadyThere(casbin_policy=casbin_policy)
    return db_item


def delete_policies_by_resource_id(
    db: Session, resource_id: str
) -> None:
    """used when deleting item"""
    query = db.query(models.CasbinRule).filter(
        and_(
            models.CasbinRule.ptype == PolicyTypeEnum.p,
            models.CasbinRule.v1 == resource_id,
        )
    )
    query.delete()
