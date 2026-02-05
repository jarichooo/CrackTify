import jwt
from datetime import datetime, timezone, timedelta
from config import Config

SECRET_KEY = Config.JWT_SECRET_KEY

def generate_jwt(user_id: int, email: str, expires_in_hours: int = 1) -> str:
    """
    Generate a JWT token for a given user using their email.

    Args:
        user_id (int): The user's ID.
        email (str): The user's email.
        expires_in_hours (int): Token expiration time in hours (default: 1 hour).

    Returns:
        str: Encoded JWT token as a string.
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token