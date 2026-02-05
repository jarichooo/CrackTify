from .api_client import post_request

async def fetch_cracks_service(user_id: int):
    """Services to fetch cracks for a user."""
    endpoint = "/cracks/fetch"
    data = {"user_id": user_id}
    response = await post_request(endpoint, data)
    return response

async def upload_crack_service(user_id: int, crack_data: dict):
    """Service to upload a new crack."""
    endpoint = "/cracks/upload"
    data = {"user_id": user_id, "crack_data": crack_data}
    response = await post_request(endpoint, data)
    return response