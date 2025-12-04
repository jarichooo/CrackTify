from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import get_profile, update_profile

router = APIRouter()

@router.get("/profile")
def api_get_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    # Placeholder implementation for fetching user profile
    auth_token = data.get("auth_token")
    
    return get_profile(auth_token, db)

@router.post("/profile/update")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    # Placeholder implementation for updating user profile
    # In a real implementation, you would verify the auth_token and update the profile in the database
    
    auth_token = data.get("auth_token")
    profile_data = data.get("profile_data", {})
    
    return update_profile(auth_token, profile_data, db)