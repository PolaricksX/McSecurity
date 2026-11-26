"""Basic password strength requirements."""
import string


def is_strong_password(password: str) -> bool:
    """Check length and character variety; this is not a guarantee of security."""
    return (
        len(password) >= 12
        and any(c in string.ascii_lowercase for c in password)
        and any(c in string.ascii_uppercase for c in password)
        and any(c in string.digits for c in password)
        and any(not c.isalnum() and not c.isspace() for c in password)
    )


REQUIREMENTS = "at least 12 characters, including an uppercase letter, a lowercase letter, a number, and a symbol"
