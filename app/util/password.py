from typing import Tuple
import hashlib, secrets


def create_hashed_password(password: str) -> Tuple[str, str]:
    """returns salt and hashed_password"""
    salt = secrets.token_hex(8)
    salted_password: str = password + salt
    return salt, hashlib.md5(salted_password.encode()).hexdigest()


def verify_password(password: str, salt: str, hashed_password: str) -> bool:
    """returns bool"""
    salted_password = password + salt
    return hashed_password == hashlib.md5(salted_password.encode()).hexdigest()
