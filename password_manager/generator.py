"""Random password generator."""
import secrets
import string


def generate_password(length: int = 16, symbols: bool = True) -> str:
    if length < 8:
        raise ValueError("length must be at least 8")
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        pools.append("!@#$%^&*()-_=+")
    chars = [secrets.choice(p) for p in pools]
    alphabet = "".join(pools)
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
