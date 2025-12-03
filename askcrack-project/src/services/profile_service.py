from typing import Dict, Any
from config import Config

from .api_client import get_request,  post_request

# Base API URL
api_url = Config.API_BASE_URL

async def get_profile(auth_token: str) -> Dict[str, Any]:
    """
    Fetch user profile using the provided auth token.
    
    Args:
        auth_token: User's authentication token
    
    Returns:
        dict: User profile data or error info
    """
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    return await get_request("/profile", headers=headers)

async def update_profile(auth_token: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user profile with the provided data.
    
    Args:
        auth_token: User's authentication token
        profile_data: Dictionary containing profile fields to update
    
    Returns:
        dict: Updated user profile data or error info
    """
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    return await post_request("/profile", data=profile_data, headers=headers)