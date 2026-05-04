from typing import Dict, Any
from config import Config

from .api_client import get_request, post_request

# Base API URL
api_url = Config.API_BASE_URL


async def get_avatar_url(user_id: int) -> Dict[str, str]:
    return await get_request(f"/profile/avatar", {"user_id": user_id})


async def update_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    return await post_request(
        f"/profile/update",
        {
            "profile_data": profile_data,
        },
    )


async def get_current_user(user_id: str) -> Dict[str, Any]:
    try:
        return await get_request(f"/profile", {"user_id": user_id})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def verify_user_password(user_id: int, old_password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/verify_password", {"user_id": user_id, "old_password": old_password}
    )


async def update_password(user_id: int, new_password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/update_password", {"user_id": user_id, "new_password": new_password}
    )


async def delete_account(user_id: int, password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/delete_account", {"user_id": user_id, "password": password}
    )

async def verify_engineer(user_id: int, license_number: str, document_path: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/verify_engineer",
        {
            "user_id": user_id,
            "license_number": license_number,
            "document_path": document_path,
        },
    )