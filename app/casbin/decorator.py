from app.casbin.enforcer import casbin_enforcer
from app.db.database import get_db
from app.exceptions.rbac import NotAuthorized
from app.schemas.user import User
from app.casbin.role_definition import ResourceActionsEnum
from app.casbin.resource_id_converter import get_resource_id_from_user_id
from flask import request
from app.util.process_request import get_user_info_from_request
from app.util.response_util import create_response
from app.config.app_config import conf
import app.repo.user as UserRepo


def authorize(action: ResourceActionsEnum = None):
    """
    Enforces authorization on all service layer with item_id and user.
    The function name must have the pattern <act>_item

    This decorator is not used on flask endpoints because it can be decoupled with
    the request path. (it does not nessisarily needs to take user/item id from request)

    when use, either use with action is not None, or admin_required is True

    THIS DECORATOR WORKS ON THE SERVICE LAYER
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


def authorize_user_domain(
    action: ResourceActionsEnum = None,
    require_casbin: bool = True,
):
    """THIS DECORATOR WORKS ON THE API LAYER"""

    def decorator(func):
        def wrapper_enforcer(*args, **kwargs):
            casbin_enforcer.load_policy()
            actor = get_user_info_from_request(request=request)

            with get_db() as db:
                db_user = UserRepo.get(db=db, item_id=actor.id)
                actor_as_user = User.from_orm(db_user)

            request.environ["actor"] = actor_as_user

            # check if the actor is xx admin if needed
            # role_ids = casbin_enforcer.get_implicit_roles_for_user(actor.id)
            # if conf.USER_ADMIN_ROLE_ID in role_ids:
            #     actor.is_blahblah_admin = True

            # try:  # no more individual resources
            #     user_id: str = kwargs["user_id"]
            #     resource_id = get_resource_id_from_user_id(user_id)
            # except:
            resource_id = conf.RESOURCE_NAME_USER
            if require_casbin:
                if casbin_enforcer.enforce(actor.id, resource_id, action):
                    print("casbin allows it..!")
                    # here i use actor because this is the initiator of the action
                    request.environ["actor"] = actor
                    return func(*args, **kwargs)
                else:
                    return create_response(
                        status_code=403,
                        message=f"User {actor.id} has no right to {action} resource {resource_id}",
                        success=False,
                    )
            else:
                return func(*args, **kwargs)

        # this is to prevent some view point!!
        wrapper_enforcer.__name__ = func.__name__
        return wrapper_enforcer

    return decorator
