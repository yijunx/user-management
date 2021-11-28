class UserDoesNotExist(Exception):
    """raised when the item is not found"""

    def __init__(self, user_id: str) -> None:
        self.message = f"用户 {user_id} 不存在"
        self.status_code = 404
        super().__init__(self.message)


class UserEmailAlreadyExist(Exception):
    """raised when user email is already there"""

    def __init__(self, email: str) -> None:
        self.message = f"用户 {email} 已经存在"
        self.status_code = 409
        super().__init__(self.message)


class UserEmailNotVerified(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = f"用户邮件尚未验证"
        self.status_code = 400
        super().__init__(self.message)


class UserEmailAlreadyVerified(Exception):
    """raised when user email is not verified"""

    def __init__(self) -> None:
        self.message = f"用户邮件已经验证"
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
        self.message = f"请使用最新的重置密码邮件中的链接"
        self.status_code = 400
        super().__init__(self.message)
