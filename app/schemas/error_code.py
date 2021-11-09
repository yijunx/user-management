from enum import Enum


class ErrorCodeEnum(int, Enum):
    """not used yet, the purpose is to return a code,
    and frontend will render a message based on the code"""

    user_login_with_password_fail = 1
    user_login_with_google_fail = 2
    user_register_fail = 3
    user_login_with_wrong_method_password = 5
    user_login_with_wrong_method_google = 6
