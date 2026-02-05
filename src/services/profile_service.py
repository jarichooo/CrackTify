from typing import Dict, Any
from config import Config

from .api_client import get_request,  post_request

# Base API URL
api_url = Config.API_BASE_URL

async def get_avatar_url(user_id: int) -> Dict[str, str]:
    return await get_request(f"/profile/avatar/{user_id}")

async def update_profile(profile_data: Dict[str, Any], new_password: str = None) -> Dict[str, Any]:
    user_id = profile_data.get("id")
    
    return await post_request(
        f"/profile/update/{user_id}",
        {
            "profile_data": profile_data,
            "new_password": new_password
        }
    )

async def verify_user_password(user_id: int, old_password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/verify_password/{user_id}",
        {
            "old_password": old_password
        }
    )

async def update_password(user_id: int, new_password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/update_password/{user_id}",
        {
            "new_password": new_password
        }
    )


async def delete_account(user_id: int, password: str) -> Dict[str, Any]:
    return await post_request(
        f"/profile/delete_account/{user_id}",
        {
            "password": password
        }
    )