from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.activity_service import fetch_recent_activity

router = APIRouter()

@router.get("/{user_id}")
def get_recent_activity(user_id: int, db: Session = Depends(get_db)):
    return fetch_recent_activity(user_id, db)