from datetime import datetime, timezone
from app.models.user import User

def get_profile(user_id: int) -> User:
    """Fetch user profile by user ID"""
    user = User.query.get(user_id)

    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    avatar_url = user.avatar_url

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "avatar_url": avatar_url
    }

def get_profile_avatar(user_id: int):
    ...

def update_profile(profile_data: dict, db) -> User:
    """Update user profile with provided data"""
    user_id = profile_data.get("id")    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {"success": True, "user": user}