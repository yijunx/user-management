from typing import Union
from sqlalchemy.sql.expression import and_
from app.casbin.role_definition import ResourceRightsEnum
from app.db.models import models
from sqlalchemy.orm import Session
from app.schemas.casbin_rule import CasbinPolicy, PolicyTypeEnum
from sqlalchemy.exc import IntegrityError
from app.exceptions.casbin_rule import PolicyIsAlreadyThere


# def __create_policy(
#     db: Session, user_id: str, resource_id: str, resource_right: ResourceRightsEnum
# ) -> models.CasbinRule:
#     """well this is not used"""
#     db_item = models.CasbinRule(
#         ptype=PolicyTypeEnum.p,
#         v0=user_id,
#         v1=resource_id,
#         v2=resource_right,
#     )
#     db.add(db_item)
#     try:
#         db.flush()
#     except IntegrityError:
#         db.rollback()
#         raise PolicyIsAlreadyThere(
#             user_id=user_id, resource_id=resource_id, resource_right=resource_right
#         )
#     return db_item


def delete_policies_by_resource_id(db: Session, resource_id: str) -> None:
    """used when deleting resource"""
    query = db.query(models.CasbinRule).filter(
        and_(
            models.CasbinRule.ptype == PolicyTypeEnum.p,
            models.CasbinRule.v1 == resource_id,
        )
    )
    query.delete()


def get_grouping(
    db: Session, role_id: str, user_id: str
) -> Union[models.CasbinRule, None]:
    db_casbin_rule = (
        db.query(models.CasbinRule)
        .filter(and_(models.CasbinRule.v0 == user_id, models.CasbinRule.v1 == role_id))
        .first()
    )
    return db_casbin_rule
