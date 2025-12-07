from datetime import datetime, timezone
from app.models.crack import Crack
from app.models.image import Image
from app.models.group import Group
from app.models.group_member import GroupMember
from app.utils.time_util import human_time

def fetch_recent_activity(user_id: int, db):
    """Fetch recent activity for a given user."""
    # Query to get recent images and cracks associated with the user
    # images = db.query(Image).filter(Image.user_id == user_id).order_by(Image.uploaded_at.desc()).limit(10).all()
    # cracks = db.query(Crack).join(Image).filter(Image.user_id == user_id).order_by(Crack.created_at.desc()).limit(10).all() 
    # activity = []

    # for image in images:
    #     activity.append({
    #         "type": "image_upload",
    #         "image_id": image.id,
    #         "uploaded_at": human_time(image.uploaded_at)
    #     })

    # for crack in cracks:
    #     activity.append({
    #         "type": "crack_created",
    #         "crack_id": crack.id,
    #         "image_id": crack.image_id,
    #         "created_at": human_time(crack.created_at)
    #     })

    # # Sort activities by date (most recent first)
    # activity.sort(key=lambda x: x.get("uploaded_at", x.get("created_at")), reverse=True)

    # return activity 
    
    # 1. Get IDs of groups the user belongs to
    group_memberships = (
        db.query(GroupMember)
        .filter(GroupMember.user_id == user_id)
        .all()
    )

    group_ids = [gm.group_id for gm in group_memberships]

    if not group_ids:
        return []  # User has no groups → no activity

    # 2. Fetch all images uploaded inside user's groups
    images = (
        db.query(Image)
        .filter(Image.group_id.in_(group_ids))
        .all()
    )

    # 3. Fetch cracks inside those same groups (via image join)
    cracks = (
        db.query(Crack)
        .join(Image, Crack.image_id == Image.id)
        .filter(Image.group_id.in_(group_ids))
        .all()
    )

    activities = []

    # ---- IMAGE UPLOAD EVENTS ----
    for img in images:
        # skip images without a group_id
        if not img.group_id:
            continue

        group = db.query(Group).filter(Group.id == img.group_id).first()

        activities.append({
            "title": "Image uploaded",
            "group": group.name if group else "Unknown Group",
            "severity": "—",
            "time": human_time(img.uploaded_at),
            "timestamp": img.uploaded_at
        })

    # ---- CRACK DETECTED EVENTS ----
    for crack in cracks:
        img = crack.image
        group = db.query(Group).filter(Group.id == img.group_id).first()

        activities.append({
            "title": "Crack detected",
            "group": group.name if group else "Unknown Group",
            "severity": crack.severity,
            "time": human_time(crack.detected_at),
            "timestamp": crack.detected_at
        })

    # Sort: newest first
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    # Remove timestamps before sending to UI
    for item in activities:
        del item["timestamp"]

    return activities