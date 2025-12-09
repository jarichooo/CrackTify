from datetime import datetime, timezone
from app.models.user import User
from app.models.crack import Crack
from app.models.group_member import GroupMember
from app.models.crack_group import CrackGroup
from app.models.group import Group

def fetch_cracks_service(group_id: int, db):
    """Fetch cracks for a specific group."""
    # Query the database to find cracks associated with the group
    cracks = db.query(Crack).join(CrackGroup).filter(CrackGroup.group_id == group_id).all()

    if not cracks:
        return {"success": False, "message": "No cracks found for this group"}

    return {
        "success": True,
        "message": "Cracks fetched successfully",
        "cracks": [crack.to_dict() for crack in cracks]
    }

def add_crack_service(user_id: int, image_base64: str, probability: float, severity: str, db):
    """Add a crack and link it to all groups where the user is a member."""

    # 1️⃣ Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}

    # 2️⃣ Find all groups the user belongs to
    user_groups = (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id)
        .all()
    )

    # 3️⃣ Create main crack record
    new_crack = Crack(
        user_id=user_id,
        image_base64=image_base64,
        probability=probability,
        severity=severity,
        detected_at=datetime.now(timezone.utc)
    )
    db.add(new_crack)
    db.flush()  # IMPORTANT! ensures new_crack.id exists before creating CrackGroup

    # 4️⃣ Link crack to all groups (many-to-many)
    for group in user_groups:
        link = CrackGroup(
            crack_id=new_crack.id,
            group_id=group.id,
            added_at=datetime.now(timezone.utc)
        )
        db.add(link)

    # 5️⃣ Commit everything
    db.commit()
    db.refresh(new_crack)

    return {
        "success": True,
        "message": "Crack added successfully",
        "crack_id": new_crack.id
    }    

def delete_crack_from_group_service(crack_id: int, group_id: int, db):
    """Delete a crack from a specific group."""
    # Check if the crack exists
    crack_group = db.query(CrackGroup).filter(
        CrackGroup.crack_id == crack_id,
        CrackGroup.group_id == group_id
    ).first()

    # Delete the crack from the group
    db.delete(crack_group)
    db.commit()

    return {"success": True, "message": "Crack deleted from group successfully"}
