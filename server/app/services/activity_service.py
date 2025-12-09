from datetime import datetime, timezone
from app.models.crack import Crack
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.user import User
from app.models.group_member import GroupMember
from app.models.crack_group import CrackGroup

from app.utils.time_util import human_time


def fetch_recent_activity(user_id: int, db):
    """Fetch recent activity for a given user."""
    # Get groups the user belongs to
    groups = db.query(Group).join(GroupMember).filter(GroupMember.user_id == user_id).all()
    group_ids = [group.id for group in groups]
    # Get recent cracks from these groups
    recent_cracks = (
        db.query(Crack)
        .join(CrackGroup, CrackGroup.crack_id == Crack.id)
        .filter(CrackGroup.group_id.in_(group_ids))
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
        location = (
            db.query(Group.name)
            .join(CrackGroup, CrackGroup.group_id == Group.id)
            .filter(CrackGroup.crack_id == crack.id)
            .first()
        )
        activity_list.append({
            "type": "crack_detected",
            "crack_id": crack.id,
            "location": location[0] if location else "Unknown location",
            "severity": crack.severity,
            "time_ago": human_time(crack.detected_at),
        })

    return {"success": True, "activities": activity_list, "overview": {"total_cracks": total_cracks, "total_severe_cracks": total_severe_cracks, "total_mild_cracks": total_mild_cracks, "total_none_cracks": total_none_cracks}}
                                                                            