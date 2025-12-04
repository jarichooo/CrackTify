import httpx
from typing import List, Dict, Any
from .api_client import get_request, post_request

async def fetch_user_groups(user_id: int) -> Dict[str, List[Any]]:
    """Fetches groups the user is a member of from the API."""
    return await get_request(f"/groups/user-groups/{user_id}")

async def fetch_groups() -> Dict[str, List[Any]]:
    """Fetches a list of groups from the API."""
    return await get_request("/groups/groups")

async def create_group(
    name: str,
    description: str | None,
    avatar_url: str | None,
    admin_id: int
) -> Dict[str, List[Any]]:
    """Creates a new group via the API."""
    data = {
        "name": name,
        "description": description,
        "avatar_url": avatar_url,
        "admin_id": admin_id
    }
    return await post_request("/groups/create-group", data)

async def join_group(user_id: int, group_id: int) -> Dict[str, Any]:
    """Adds a user to a group via the API."""
    data = {
        "user_id": user_id,
        "group_id": group_id
    }
    return await post_request("/groups/join-group", data) 