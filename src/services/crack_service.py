from .api_client import post_request


async def fetch_cracks_service(user_id: int, limit=0):
    """Service to fetch cracks for a user."""
    try:
        return await post_request("/cracks/fetch", {"user_id": user_id, "limit": limit})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def fetch_one_crack(crack_id: int):
    """Service to fetch details of a specific crack."""
    try:
        return await post_request("/cracks/get-one", {"crack_id": crack_id})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def detect_crack(
    file_info: dict[str, any], confidence_threshold: float = 0.5, timeout: int = 60
):
    """Service to detect cracks in an image."""
    try:
        return await post_request(
            "/cracks/detect",
            {"file_info": file_info, "confidence_threshold": confidence_threshold},
            timeout=timeout,
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def add_crack_service(user_id: int, crack_data: dict):
    """Service to add a new crack."""
    try:
        return await post_request(
            "/cracks/add", {"user_id": user_id, "crack_data": crack_data}
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def update_crack_service(crack_id: int, crack_data: dict):
    """Service to update a crack file."""
    try:
        return await post_request(
            "/cracks/update", {"crack_id": crack_id, "updated_data": crack_data}
        )

    except Exception as e:
        return {"success": False, "message": str(e)}


async def can_edit_crack(user_id: int, crack_id: int):
    try:
        return await post_request(
            f"/cracks/can_edit_by", {"crack_id": crack_id, "user_id": user_id}
        )
    except Exception as e:
        return {"success": False, "message": str(e)}


async def delete_crack_service(crack_id: int):
    """Service to delete a crack."""
    try:
        return await post_request("/cracks/delete", {"crack_id": crack_id})

    except Exception as e:
        return {"success": False, "message": str(e)}
