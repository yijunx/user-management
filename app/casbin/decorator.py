from app.casbin.enforcer import casbin_enforcer
from app.exceptions.rbac import NotAuthorized
from app.schemas.user import User
from app.casbin.role_definition import ResourceActionsEnum
from app.casbin.resource_id_converter import get_resource_id_from_user_id
from flask import request
from app.util.process_request import get_user_info_from_request
from app.util.response_util import create_response
from app.config.app_config import conf


def authorize(action: ResourceActionsEnum = None):
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


def authorize_user_domain(action: ResourceActionsEnum = None):
    def decorator(func):
        def wrapper_enforcer(*args, **kwargs):
            user = get_user_info_from_request(request=request)
            try:
                user_id: str = kwargs["user_id"]
                resource_id = get_resource_id_from_user_id(user_id)
            except:
                resource_id = conf.RESOURCE_NAME_USER

            if casbin_enforcer.enforce(user_id, resource_id, action):
                print("casbin allows it..!")
                return func(*args, **kwargs, user=user)
            else:
                return create_response(
                    status_code=403,
                    message=f"User {user.id} has no right to {action} resource {resource_id}",
                    success=False,
                )
        return wrapper_enforcer
    return decorator

