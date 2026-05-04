from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """Get hashed password.

    Args:
        password: textual form of password

    Returns: hashed password
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare password and password hash.

    Args:
        plain_password: textual form of password
        hashed_password: password hash

    Returns: True if passwords match, otherwise False
    """
    return password_hash.verify(plain_password, hashed_password)
