from typing import Dict, Any
from .api_client import post_request, get_request


async def check_uniqueness(field: str, check_type: str = "email") -> Dict[str, Any]:
    """Checks the uniqueness of a field (email or username)."""
    try:
        return await post_request("/auth/check-uniqueness", {"field": field, "check_type": check_type})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def register_user(
    first_name: str, last_name: str, username: str, email: str, password: str, is_engineer: bool = False
) -> Dict[str, Any]:
    """Registers a new user with the provided details."""
    try:
        return await post_request(
            "/auth/register",
            {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email_address": email,
                "password": password,
                "is_engineer": is_engineer,  # Default to False, can be updated based on user selection in the registration form
            },
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def login_user(user: str, password: str) -> Dict[str, Any]:
    """Logs in a user with the provided username or email and password."""
    try:
        return await post_request(
            "/auth/login", {"user": user, "password": password}
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def forgot_password(email: str, new_password: str) -> Dict[str, Any]:
    """Resets the password for a user with the provided email."""
    try:
        return await post_request(
            "/auth/forgot-password",
            {"email_address": email, "new_password": new_password},
        )

    except Exception as e:
        return {"success": False, "message": str(e)}
