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

def update_profile(user_id: int, profile_data: dict) -> User:
    """Update user profile with provided data"""
    user = User.query.get(user_id)

    user.first_name = profile_data.get("first_name", user.first_name)
    user.last_name = profile_data.get("last_name", user.last_name)
    user.email = profile_data.get("email", user.email)
    user.avatar_url = profile_data.get("avatar_url", user.avatar_url)

    user.save()

    return user