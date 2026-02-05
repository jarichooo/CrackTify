from datetime import datetime, timezone
from app.models.crack import Crack
from app.models.user import User
from app.utils.time_util import human_time


def fetch_recent_activity(user_id: int, db):
    """Fetch recent crack activity for a given user."""

    # Get recent cracks directly tied to the user
    recent_cracks = (
        db.query(Crack)
        .filter(Crack.user_id == user_id)
        .order_by(Crack.detected_at.desc())
        .limit(20)
        .all()
    )

    activity_list = []

    total_cracks = len(recent_cracks)
    total_severe_cracks = sum(1 for crack in recent_cracks if crack.severity == "Severe")
    total_mild_cracks = sum(1 for crack in recent_cracks if crack.severity == "Mild")
    total_none_cracks = sum(1 for crack in recent_cracks if crack.severity == "None")

    for crack in recent_cracks:
        activity_list.append({
            "type": "Crack detected",
            "crack_id": crack.id,
            "location": "User-specific",  # simplified since groups are removed
            "severity": crack.severity,
            "time_ago": human_time(crack.detected_at),
        })

    return {
        "success": True,
        "activities": activity_list,
        "overview": {
            "total_cracks": total_cracks,
            "total_severe_cracks": total_severe_cracks,
            "total_mild_cracks": total_mild_cracks,
            "total_none_cracks": total_none_cracks,
        }
    }