from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.group_service import create_group_service, fetch_groups_service, join_group_service, fetch_user_groups_service, fetch_group_info_service, edit_member_service, remove_member_service

router = APIRouter()

@router.post("/create-group")
def api_create_group(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to create a new group."""
    name = data.get("name")
    pin = data.get("pin")
    admin_id = data.get("admin_id")
    
    return create_group_service(name, pin, admin_id, db)

@router.post("/join-group")
def api_join_group(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint for a user to join a group."""
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    
    return join_group_service(user_id, group_id, db)

@router.get("/group-info/{group_id}")
def api_fetch_group_info(group_id: int, db: Session = Depends(get_db)):
    """Endpoint to fetch detailed information about a specific group."""
    return fetch_group_info_service(group_id, db)

@router.get("/user-groups/{user_id}")
def api_fetch_user_groups(user_id: int, db: Session = Depends(get_db)):
    """Endpoint to fetch groups a user is a member of."""
    return fetch_user_groups_service(user_id, db)

@router.post("/all")
def api_fetch_groups(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to fetch all groups."""
    user_id = data.get("user_id")

    return fetch_groups_service(user_id, db)

@router.post("/edit-member")
def api_edit_member(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to edit a group member's role."""
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    new_role = data.get("new_role")

    return edit_member_service(user_id, group_id, new_role, db) 

@router.post("/remove-member")
def api_remove_member(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to remove a user from a group."""
    user_id = data.get("user_id")
    group_id = data.get("group_id")

    return remove_member_service(user_id, group_id, db)