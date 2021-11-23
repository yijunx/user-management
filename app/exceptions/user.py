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


class UserEmailNotVerified(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = f"Email is not verified"
        self.status_code = 400
        super().__init__(self.message)


class UserEmailAlreadyVerified(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = f"Email already verified"
        self.status_code = 400
        super().__init__(self.message)


class UserPasswordResetNotSame(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = f"Passwords not match"
        self.status_code = 400
        super().__init__(self.message)


class UserPasswordResetSaltNotMatch(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = (
            f"Please check if this is the latest emailed link for resetting password"
        )
        self.status_code = 400
        super().__init__(self.message)
