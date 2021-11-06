from app.casbin.role_definition import ResourceRightsEnum
from app.schemas.casbin_rule import CasbinPolicy


class PolicyDoesNotExist(Exception):
    """raised when the policy is not found (when deleting)"""

    def __init__(self, user_id: str, resource_id: str) -> None:
        self.message = f"Resouce {resource_id} for user {user_id} does not exist"
        self.status_code = 404
        super().__init__(self.message)


class PolicyIsAlreadyThere(Exception):
    """raised when the v0 and v1 duplicates (when sharing)"""

    def __init__(
        self, user_id: str, resource_id: str, resource_right: ResourceRightsEnum
    ) -> None:
        self.message = (
            f"{user_id}'s right on {resource_id} is already there ({resource_right})"
        )
        self.status_code = 409
        super().__init__(self.message)
