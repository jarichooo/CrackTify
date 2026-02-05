from datetime import datetime, timezone
from app.models.user import User
from app.utils.password import hash_password, verify_password
from app.utils.pdf import generate_user_pdf


def update_profile(profile_data: dict, new_password, db):
    """Update user profile with provided data"""
    user_id = profile_data.get("id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    if new_password:
        user.password_hash = hash_password(new_password)

    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    print("Updated user profile:", user)

    return {"success": True, "user": user}


def verify_user_password(user_id: int, old_password: str, db):
    """Verify if the provided password matches the user's password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    if verify_password(old_password, user.password_hash):
        return {"success": True, "message": "Password verified"}
    else:
        return {"success": False, "error": "Incorrect password"}


def download_data(user_id: int, db):
    """Download user data"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    generated_pdf_path = f"user_{user_id}_data.pdf"
    generate_user_pdf(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "joined_at": user.created_at.strftime("%Y-%m-%d"),
            # "scans_done": user.scans_done,
            # "cracks_detected": user.cracks_detected,
            # "last_scan": user.last_scan.strftime("%Y-%m-%d") if user.last_scan else "N/A",
        },
        output_path=generated_pdf_path
    )
    with open(generated_pdf_path, "rb") as pdf_file:
        pdf_content = pdf_file.read()

    return pdf_content


def delete_account(user_id: int, password: str, db):
    """Delete user account after verifying the password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    if not verify_password(password, user.password_hash):
        return {"success": False, "error": "Incorrect password"}

    # Delete the user account directly (no group logic)
    db.delete(user)
    db.commit()

    return {"success": True, "message": "Account deleted successfully"}