from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.utils.password import hash_password, verify_password
from app.utils.token_generator import generate_jwt

def check_email_unique_service(email: str, db):
    """Check if the email is already registered."""
    # Query the database to find a user with the given email
    user = db.query(User).filter(User.email == email).first()

    if user:
        return {"success": False, "message": "Email is already registered"} # If email found, return not unique
    
    return {"success": True, "message": "Email is unique"}

def register_user_service(first_name: str, last_name: str, email: str, password: str, db):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"success": False, "message": "User already exists"}

    # Hash the password
    hashed_password = hash_password(password)

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(new_user)
    db.commit()

    token = generate_jwt(new_user.id, new_user.email)

    return {"success": True, "message": "User registered successfully", "token": token}

def login_user_service(email: str, password: str, db):
    """Authenticate a user by email and password."""
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "Invalid email or password"}

    # Verify password
    if not verify_password(password, user.password_hash):
        return {"success": False, "message": "Invalid email or password"}
    
    token = generate_jwt(user.id, user.email)

    return {"success": True, "message": "Login successful", "token": token}
