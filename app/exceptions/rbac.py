class NotAuthorized(Exception):
    def __init__(self, resource_id: str, action: str, user_id: str) -> None:
        self.status_code = 403
        self.message = f"Not authorized. user: {user_id}, resource_id: {resource_id}, action: {action}"
        super().__init__(self.message)


class NotAuthorizedAdminOnly(Exception):
    def __init__(self, user_id: str) -> None:
        self.status_code = 403
        self.message = f"Not authorized. user: {user_id} is not admin"
        super().__init__(self.message)
