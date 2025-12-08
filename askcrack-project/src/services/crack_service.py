from .api_client import post_request

def fetch_cracks_service(group_id: int):
    """Service to fetch cracks for a specific group."""
    payload = {"group_id": group_id}
    response = post_request("/fetch-cracks", payload)
    return response

def add_crack_service(user_id: int, image_base64: str, probability: float, severity: str):
    """Service to add a new crack."""
    payload = {
        "user_id": user_id,
        "image_base64": image_base64,
        "probability": probability,
        "severity": severity,
    }
    response = post_request("/add-crack", payload)
    return response

def delete_crack_service(crack_id: int, user_id: int):
    """Service to delete a crack."""
    payload = {
        "crack_id": crack_id,
        "user_id": user_id
    }
    response = post_request("/delete-crack", payload)
    return response

def change_crack_visibility_service(crack_id: int, visibility: bool):
    """Service to change the visibility of a crack."""
    payload = {
        "crack_id": crack_id,
        "visibility": visibility
    }
    response = post_request("/change-crack-visibility", payload)
    return response