from typing import Dict, Any
from config import Config

from .api_client import get_request,  post_request

# Base API URL
api_url = Config.API_BASE_URL

async def get_avatar_url(user_id: int) -> Dict[str, str]:
    return await get_request(f"/profile/avatar/{user_id}")

async def update_profile(user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    return await post_request(
        f"/profile/update/{user_id}",
        {
            "user_id": user_id,
            "profile_data": profile_data
        }
    )