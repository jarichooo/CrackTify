from datetime import datetime, timezone, timedelta
from app.models.group import Group
from app.models.group_member import GroupMember


# ---------------------------------------------------------
# CREATE GROUP
# ---------------------------------------------------------
def create_group_service(
    name: str,
    description: str | None,
    avatar_url: str | None,
    admin_id: int,
    db
):
    """Create a group and add admin as member."""
    new_group = Group(
        name=name,
        description=description,
        avatar_url=avatar_url,
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



# ---------------------------------------------------------
# JOIN GROUP
# ---------------------------------------------------------
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



# ---------------------------------------------------------
# FETCH USER'S GROUPS
# ---------------------------------------------------------
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
            "description": g.description,
            "avatar_url": g.avatar_url,
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



# ---------------------------------------------------------
# FETCH GROUPS USER IS NOT A MEMBER OF
# ---------------------------------------------------------
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
            "description": g.description,
            "avatar_url": g.avatar_url,
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
