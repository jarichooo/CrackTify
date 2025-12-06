import httpx
from typing import List, Dict, Any
from .api_client import get_request, post_request

async def fetch_user_groups(user_id: int) -> Dict[str, List[Any]]:
    """Fetches groups the user is a member of from the API."""
    return await get_request(f"/groups/user-groups/{user_id}")

async def fetch_groups(user_id: int) -> Dict[str, List[Any]]:
    """Fetches a list of groups from the API."""
    return await post_request("/groups/all", {"user_id": user_id})

async def fetch_group_info(group_id: int) -> Dict[str, Any]:
    """Fetches detailed information about a specific group via the API."""
    return await get_request(f"/groups/group-info/{group_id}")

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

async def edit_member(user_id: int, group_id: int, new_role: str) -> Dict[str, Any]:
    """Edits a group member's role via the API."""
    data = {
        "user_id": user_id,
        "group_id": group_id,
        "new_role": new_role
    }
    return await post_request("/groups/edit-member", data)

async def remove_member(user_id: int, group_id: int) -> Dict[str, Any]:
    """Removes a user from a group via the API."""
    data = {
        "user_id": user_id,
        "group_id": group_id
    }
    return await post_request("/groups/remove-member", data)