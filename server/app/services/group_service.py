from datetime import datetime, timezone, timedelta
from app.models.group import Group
from app.models.group_member import GroupMember


# CREATE GROUP
def create_group_service(
    name: str,
    pin: int,
    admin_id: int,
    db
):
    """Create a group and add admin as member."""
    new_group = Group(
        name=name,
        pin=pin,
        admin_id=admin_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # Add admin as member
    new_member = GroupMember(
        group_id=new_group.id,
        user_id=admin_id,
        joined_at=datetime.now(timezone.utc)
    )

    db.add(new_member)
    db.commit()

    return fetch_user_groups_service(admin_id, db)

# JOIN GROUP
def join_group_service(user_id: int, group_id: int, db):
    """User joins a group."""

    # Check if already member
    existing = db.query(GroupMember).filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if existing:
        return {"success": False, "message": "User already a member of the group."}

    new_member = GroupMember(
        user_id=user_id,
        group_id=group_id,
        joined_at=datetime.now(timezone.utc)
    )

    db.add(new_member)
    db.commit()

    return fetch_user_groups_service(user_id, db)

# FETCH USER'S GROUPS
def fetch_user_groups_service(user_id: int, db):
    """Fetch groups a user is a member of."""
    groups = (
        db.query(Group)
        .join(GroupMember)
        .filter(GroupMember.user_id == user_id)
        .all()
    )

    result = []

    for g in groups:
        result.append({
            "id": g.id,
            "name": g.name,
            "pin": g.pin,
            "admin_id": g.admin_id,
            "created_at": g.created_at.isoformat(),

            # FIXED: g.members is a list of GroupMember objects (not users)
            "members": [
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "joined_at": member.joined_at.isoformat()
                }
                for member in g.members
            ]
        })

    return {"groups": result}

# FETCH GROUPS USER IS NOT A MEMBER OF
def fetch_groups_service(user_id: int, db):
    """Fetch groups the user is NOT a member of."""

    groups = (
        db.query(Group)
        .filter(~Group.members.any(GroupMember.user_id == user_id))
        .all()
    )

    result = []

    for g in groups:
        result.append({
            "id": g.id,
            "name": g.name,
            "pin": g.pin,
            "admin_id": g.admin_id,
            "created_at": g.created_at.isoformat(),

            # Return group members correctly
            "members": [
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "joined_at": member.joined_at.isoformat()
                }
                for member in g.members
            ]
        })

    return {"groups": result}

def fetch_group_info_service(group_id: int, db):
    """Fetch detailed information about a specific group."""
    g = db.query(Group).filter_by(id=group_id).first()

    if not g:
        return {"success": False, "message": "Group not found."}

    group_info = {
        "id": g.id,
        "name": g.name,
        "pin": g.pin,
        "admin_id": g.admin_id,
        "created_at": g.created_at.isoformat(),
        "members": [
            {
                "user_id": member.user_id,
                "first_name": member.user.first_name,
                "last_name": member.user.last_name,
                "joined_at": member.joined_at.isoformat()
            }
            for member in g.members
        ]
    }

    return {"group": group_info}

def edit_member_service(user_id: int, group_id: int, new_role: str, db):
    """Edit a group member's role."""
    member = db.query(GroupMember).filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if not member:
        return {"success": False, "message": "Member not found in the group."}

    member.role = new_role
    db.commit()

    return {"success": True, "message": "Member role updated successfully."}

def remove_member_service(user_id: int, group_id: int, db):
    """Remove a user from a group."""
    member = db.query(GroupMember).filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if not member:
        return {"success": False, "message": "Member not found in the group."}

    db.delete(member)
    db.commit()

    if user_id == db.query(Group).filter_by(id=group_id).first().admin_id:
        # If the admin leaves, delete the group
        db.query(Group).filter_by(id=group_id).delete()
        db.commit()

    return {"success": True, "message": "Member removed from the group successfully."}