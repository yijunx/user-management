class UserDoesNotExist(Exception):
    """raised when the item is not found"""

    def __init__(self, user_id: str) -> None:
        self.message = f"User {user_id} does not exist"
        self.status_code = 404
        super().__init__(self.message)


class UserEmailAlreadyExist(Exception):
    """raised when user email is already there"""

    def __init__(self, email: str) -> None:
        self.message = f"User with email {email} already exists"
        self.status_code = 409
        super().__init__(self.message)
