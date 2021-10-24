class UserDoesNotExist(Exception):
    """raised when the item is not found"""

    def __init__(self, user_id: str) -> None:
        self.message = f"User {user_id} does not exist"
        self.status_code = 404
        super().__init__(self.message)

