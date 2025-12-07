from datetime import datetime, timezone
from app.models.user import User
from app.models.crack import Crack
from app.models.group_member import GroupMember
from app.models.group import Group

def fetch_cracks_service(group_id: int, db):
    """Fetch all visible cracks for the specified group."""
    cracks = db.query(Crack).filter(Crack.group_id == group_id, Crack.visibility == True).all()
    
    crack_list = []
    for crack in cracks:
        crack_list.append({
            "id": crack.id,
            "user_id": crack.user_id,
            "group_id": crack.group_id,
            "image_base64": crack.image_base64,
            "severity": crack.severity,
            "detected_at": crack.detected_at.isoformat()
        })
    
    return {"success": True, "cracks": crack_list}

def add_crack_service(user_id: int, image_base64: str, db):
    """Add a new crack visible to ALL groups the user belongs to."""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    cracks_created = []

    # Create crack per group
    for group in user.groups:
        crack = Crack(
            user_id=user_id,
            group_id=group.id,
            image_base64=image_base64,
            visibility=True
        )
        db.add(crack)
        cracks_created.append(crack)

    # Optional private crack
    private = Crack(
        user_id=user_id,
        group_id=None,
        image_base64=image_base64,
        visibility=False
    )
    db.add(private)
    cracks_created.append(private)

    db.commit()

    return {"success": True, "cracks_added": len(cracks_created)}

def delete_crack_service(crack_id: int, user_id: int, db):
    """Delete a crack if it belongs to the user. or admin of the group."""
    crack = db.query(Crack).filter(Crack.id == crack_id).first()
    if not crack:
        return {"success": False, "message": "Crack not found"}

    # Check ownership or admin rights
    if crack.user_id != user_id:
        # Check if user is admin of the group
        if crack.group_id:
            group = db.query(Group).filter(Group.id == crack.group_id).first()
            if not group or group.admin_id != user_id:
                return {"success": False, "message": "Unauthorized to delete this crack"}
        else:
            return {"success": False, "message": "Unauthorized to delete this crack"}

    db.delete(crack)
    db.commit()

    return {"success": True, "message": "Crack deleted successfully"}

def change_crack_visibility_service(crack_id: int, visibility: bool, db):
    """Change the visibility of a crack."""
    crack = db.query(Crack).filter(Crack.id == crack_id).first()
    if not crack:
        return {"success": False, "message": "Crack not found"}

    crack.visibility = visibility
    db.commit()

    return {"success": True, "message": "Crack visibility updated"}