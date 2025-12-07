from ast import Dict
from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import get_profile, update_profile

router = APIRouter()

@router.get("/avatar/{user_id}")
def api_get_avatar_url(user_id):
    return 

@router.post("/update/{user_id}")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    profile_data = data.get("profile_data", {})

    return update_profile(profile_data, db)