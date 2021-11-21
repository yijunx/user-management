from enum import Enum


class RoleNameEnum(str, Enum):
    # well we could have more admin types in the future
    #
    WORD_MANAGEMENT_ADMIN = "word_management_admin"


class PolicyTypeEnum(str, Enum):
    """p for policy, g for grouping"""

    p = "p"
    g = "g"


class ResourceRightsEnum(str, Enum):
    """one user of one resource can only be one of the below"""

    own = "own_right"  # user is owner of the user resource
    admin = "admin_right"  # user is admin


class ResourceActionsEnum(str, Enum):
    """these are the actions"""

    # used when user view his detail page
    get_detail = "get_detail"
    # used when user update name or password or other profile
    patch_detail = "patch_detail"
    # used when user wants to delete himself...
    unregister = "unregister"
    # used when user wants to list users and search
    list_users = "list_users"
    # used when admin wants to create a user
    create_user = "create_user"
    # used when admin wants to (un)ban a user
    ban_user = "ban_user"
    unban_user = "unban_user"
    delete_user = "delete_user"
    manage_role_for_user = "manage_role_for_user"


# this is dynamic
# this is make sure that, own covers edit, edit covers view
# this also supports other relations, very customization
resource_right_action_mapping: dict = {
    ResourceRightsEnum.own: {
        ResourceActionsEnum.get_detail,
        ResourceActionsEnum.patch_detail,
        ResourceActionsEnum.unregister,
        ResourceActionsEnum.list_users,
    },
    ResourceRightsEnum.admin: {
        ResourceActionsEnum.get_detail,
        # admin cannot change people's password or name..
        # ResourceActionsEnum.patch_detail,
        # admin cannot unregister user
        # ResourceActionsEnum.unregister,
        ResourceActionsEnum.list_users,
        ResourceActionsEnum.create_user,
        ResourceActionsEnum.ban_user,
        ResourceActionsEnum.unban_user,
        ResourceActionsEnum.delete_user,
        ResourceActionsEnum.manage_role_for_user,
    },
}
