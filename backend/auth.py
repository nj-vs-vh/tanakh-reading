import secrets
from hashlib import sha256

from backend import config


def hash_password(password: str, salt: str) -> str:
    h = sha256()
    h.update(password.encode("utf-8"))
    h.update(salt.encode("utf-8"))
    h.update(config.PEPPER)
    return h.hexdigest()


def generate_signup_token() -> str:
    return secrets.token_urlsafe(24)
