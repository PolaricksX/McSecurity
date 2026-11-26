"""Shared password strength requirements."""


REQUIREMENTS = (
    "Use at least 12 characters, including an uppercase letter, a lowercase "
    "letter, a number, and a non-whitespace symbol."
)


def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 12
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and any(not char.isalnum() and not char.isspace() for char in password)
    )
