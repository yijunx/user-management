from app.casbin.enforcer import casbin_enforcer
from app.exceptions.rbac import NotAuthorized
from app.schemas.user import User
from app.casbin.role_definition import SpecificResourceActionsEnum
from app.casbin.resource_id_converter import get_resource_id_from_user_id


def authorize(action: SpecificResourceActionsEnum = None):
    """
    Enforces authorization on all service layer with item_id and user.
    The function name must have the pattern <act>_item

    This decorator is not used on flask endpoints because it can be decoupled with
    the request path. (it does not nessisarily needs to take user/item id from request)

    when use, either use with action is not None, or admin_required is True
    """

    def decorator(func):
        def wrapper_enforcer(*args, **kwargs):
            user: User = kwargs["user"]
            # now user is not admin
            item_id: str = kwargs["item_id"]
            resource_id: str = get_resource_id_from_user_id(item_id)
            if casbin_enforcer.enforce(user.id, resource_id, action):
                print("casbin allows it..!")
                return func(*args, **kwargs)
            else:
                raise NotAuthorized(resource_id=item_id, action=action, user_id=user.id)

        return wrapper_enforcer

    return decorator
