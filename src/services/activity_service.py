from .api_client import get_request

async def fetch_recent_activity_service(user_id: int):
    """Fetch recent activity for a given user."""
    return await get_request(f"/activities/{user_id}")