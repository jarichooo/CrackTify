from .api_client import post_request

async def fetch_cracks_service(user_id: int):
    """Service to fetch cracks for a user."""
    try:
        return await post_request(
            "/cracks/fetch", 
            {
                "user_id": user_id
            }
        )
    
    except Exception as e:
        return {"success": False, "message": str(e)}

async def add_crack_service(user_id: int, crack_data: dict):
    """Service to add a new crack."""
    try:
        return await post_request(
            "/cracks/add",
            {
                "user_id": user_id,
                "crack_data": crack_data
            }
        )
    
    except Exception as e:
        return {"success": False, "message": str(e)}