from typing import Dict, Any
from config import Config

from .api_client import get_request, post_request


async def get_notifications(user_id: int) -> Dict[str, Any]:
    """Fetches notifications for the given user ID."""
    try:
        return await get_request(f"/notifications", {"user_id": user_id})

    except Exception as e:
        return {"success": False, "message": str(e)}


async def mark_notification_as_read(notification_id: int, is_read: bool = True) -> dict:
    return await post_request(
        "/notifications/mark-read",
        {
            "notification_id": notification_id,
            "is_read": is_read,  # ← lets server set either state
        },
    )


async def delete_notification(notification_id: int) -> Dict[str, Any]:
    """Deletes a notification."""
    try:
        return await post_request(
            f"/notifications/delete", {"notification_id": notification_id}
        )

    except Exception as e:
        return {"success": False, "message": str(e)}
