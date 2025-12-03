from typing import Dict, Any
from .api_client import post_request

async def check_email_unique(email: str) -> Dict[str, Any]:
    return await post_request(
        "/auth/check-email",
        {
            "email": email
        }
    )

async def register_user(first_name: str, last_name: str, email: str, password: str) -> Dict[str, Any]:
    return await post_request(
        "/auth/register",
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        }
    )

async def login_user(email: str, password: str) -> Dict[str, Any]:
    return await post_request(
        "/auth/login",
        {
            "email": email,
            "password": password
        }
    )
