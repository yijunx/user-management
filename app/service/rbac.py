from enum import Enum
from app.config.app_config import conf
from app.db.database import get_db
import app.repo.user as UserRepo
import app.repo.casbin as CasbinRepo
import requests
from app.schemas.pagination import QueryPagination
from app.schemas.response import StandardResponse
from app.schemas.casbin_rule import CasbinRuleWithPaging
from app.schemas.user import UserWithPaging, User, UserInResponse


# well do we need these?
class ServiceEnum(str, Enum):
    word_management = "word_management"
    user_management = "user_management"


service_to_rbac_endpoint_mapping = {
    ServiceEnum.word_management: conf.WORD_MANAGEMENT_RBAC_URL
}


def add_admin(service: ServiceEnum, user_id: str):
    with get_db() as db:
        db_user = UserRepo.get(db=db, item_id=user_id)

        if db_user.banned:
            raise Exception("user banned already..")

        r = requests.post(
            url=service_to_rbac_endpoint_mapping[service],
            json={"id": db_user.id, "name": db_user.name, "email": db_user.email},
        )
        assert r.status_code == 200
        response = StandardResponse(r.json()["response"])
        if not response.success:
            raise Exception(f"add admin failed with message {response.message}")


def remove_admin(service: str, user_id: str):
    r = requests.delete(url=f"{service_to_rbac_endpoint_mapping[service]}/{user_id}")
    assert r.status_code == 200
    response = StandardResponse(r.json()["response"])
    if not response.success:
        raise Exception("remove admin failed")


def list_admin(service: str, query_pagination: QueryPagination) -> UserWithPaging:
    r = requests.get(
        url=service_to_rbac_endpoint_mapping[service], params=query_pagination.dict()
    )
    assert r.status_code == 200
    casbin_rule_with_paging = CasbinRuleWithPaging(**r.json()["response"])
    with get_db() as db:
        db_users = UserRepo.get_all_without_pagination(
            db=db, item_ids=[x.v0 for x in casbin_rule_with_paging.data]
        )
        users = [User.from_orm(x) for x in db_users]
    return UserWithPaging(
        data=[UserInResponse(**x.dict()) for x in users],
        paging=casbin_rule_with_paging.paging,
    )


def is_admin(service: str, user_id: str) -> bool:
    r = requests.get(url=f"{service_to_rbac_endpoint_mapping[service]}/{user_id}")
    if r.status_code == 200:
        return True
    return False


def is_admin_here(user_id: str) -> bool:
    with get_db() as db:
        db_policy = CasbinRepo.get_grouping(
            db=db, role_id=conf.USER_ADMIN_ROLE_ID, user_id=user_id
        )
        if db_policy:
            return True
    return False


def admin_check(user_id: str) -> dict:
    is_word_service_admin = is_admin(
        service=ServiceEnum.word_management, user_id=user_id
    )
    is_user_service_admin = is_admin_here(user_id=user_id)
    return {
        ServiceEnum.word_management: is_word_service_admin,
        ServiceEnum.user_management: is_user_service_admin,
    }
