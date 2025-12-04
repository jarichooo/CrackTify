from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.group_service import create_group_service, fetch_groups_service, join_group_service, fetch_user_groups_service

router = APIRouter()

@router.post("/create-group")
def api_create_group(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to create a new group."""
    name = data.get("name")
    description = data.get("description", None)
    avatar_url = data.get("avatar_url", None)
    admin_id = data.get("admin_id")
    
    return create_group_service(name, description, avatar_url, admin_id, db)

@router.post("/join-group")
def api_join_group(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint for a user to join a group."""
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    
    return join_group_service(user_id, group_id, db)

@router.get("/user-groups/{user_id}")
def api_fetch_user_groups(user_id: int, db: Session = Depends(get_db)):
    """Endpoint to fetch groups a user is a member of."""
    return fetch_user_groups_service(user_id, db)

@router.get("/groups")
def api_fetch_groups(db: Session = Depends(get_db)):
    """Endpoint to fetch all groups."""
    return fetch_groups_service(db)