from enum import Enum


class ErrorCodeEnum(int, Enum):
    user_login_with_password_fail = 1
    user_login_with_google_fail= 2
    user_register_fail = 3
    user_login_with_wrong_method_password = 4
    user_login_with_wrong_method_google = 4

