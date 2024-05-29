import re

def validate_password(password: str) -> str:
    pattern = re.compile(
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
    )
    if not pattern.match(password):
        raise ValueError(
            "Password must contain at least 1 uppercase letter, "
            "1 lowercase letter, 1 number, and 1 special character."
        )
    return password
