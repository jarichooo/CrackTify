from typing import Dict, Any
from .api_client import post_request, get_request


async def check_email_unique(email: str) -> Dict[str, Any]:
    try:
        return await post_request("/auth/check-email", {"email_address": email})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def register_user(
    first_name: str, last_name: str, email: str, password: str
) -> Dict[str, Any]:
    try:
        return await post_request(
            "/auth/register",
            {
                "first_name": first_name,
                "last_name": last_name,
                "email_address": email,
                "password": password,
            },
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def login_user(email: str, password: str) -> Dict[str, Any]:
    try:
        return await post_request(
            "/auth/login", {"email_address": email, "password": password}
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def forgot_password(email: str, new_password: str) -> Dict[str, Any]:
    try:
        return await post_request(
            "/auth/forgot-password",
            {"email_address": email, "new_password": new_password},
        )

    except Exception as e:
        return {"success": False, "message": str(e)}
