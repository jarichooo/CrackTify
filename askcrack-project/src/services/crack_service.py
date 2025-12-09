from .api_client import post_request

async def fetch_cracks_service(group_id: int):
    """Service to fetch cracks for a specific group."""
    payload = {"group_id": group_id}
    response = await post_request("/cracks/fetch-cracks", payload)
    return response

async def add_crack_service(user_id: int, image_base64: str, probability: float, severity: str):
    """Service to add a new crack."""
    payload = {
        "user_id": user_id,
        "image_base64": image_base64,
        "probability": probability,
        "severity": severity,
    }
    response = await post_request("/cracks/add-crack", payload)
    return response

async def delete_crack_from_group_service(crack_id: int, group_id: int):
    """Service to delete a crack from a specific group."""
    payload = {
        "crack_id": crack_id,
        "group_id": group_id
    }
    response = await post_request("/cracks/delete-crack-from-group", payload)
    return response