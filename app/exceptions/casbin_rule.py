from app.schemas.casbin_rule import CasbinPolicy


class PolicyDoesNotExist(Exception):
    """raised when the policy is not found (when deleting)"""

    def __init__(self, user_id: str, resource_id: str) -> None:
        self.message = f"Resouce {resource_id} for user {user_id} does not exist"
        self.status_code = 404
        super().__init__(self.message)


class PolicyIsAlreadyThere(Exception):
    """raised when the v0 and v1 duplicates (when sharing)"""

    def __init__(self, casbin_policy: CasbinPolicy) -> None:
        self.message = (
            f"{casbin_policy.v0}'s right on {casbin_policy.v1} is already there"
        )
        self.status_code = 409
        super().__init__(self.message)