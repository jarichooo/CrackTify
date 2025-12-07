from datetime import datetime, timezone
from app.models.crack import Crack
from app.models.group import Group
from app.models.group_member import GroupMember
from app.utils.time_util import human_time

def fetch_recent_activity(user_id: int, db):
    """Fetch recent activity for a given user."""
    # Get groups the user belongs to
    group_memberships = db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    group_ids = [membership.group_id for membership in group_memberships]

    # Fetch recent cracks in these groups
    recent_cracks = db.query(Crack).filter(
        Crack.group_id.in_(group_ids)
    ).order_by(Crack.detected_at.desc()).limit(20).all()

    activity_list = []
    for crack in recent_cracks:
        activity_list.append({
            "type": "crack_detected",
            "crack_id": crack.id,
            "group_id": crack.group_id,
            "user_id": crack.user_id,
            "detected_at": crack.detected_at.isoformat(),
            "time_ago": human_time(crack.detected_at)
        })

    return {"success": True, "activities": activity_list}