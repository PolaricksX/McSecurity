"""Key derivation and encryption helpers."""
import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 600_000


def new_salt() -> bytes:
    return os.urandom(16)


def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def encrypt(key: bytes, data: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt(key: bytes, token: bytes) -> bytes:
    """Raise ValueError when the key is wrong or data is corrupted."""
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Wrong master password or corrupted vault") from exc
