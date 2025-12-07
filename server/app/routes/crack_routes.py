from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.crack_service import fetch_cracks_service, add_crack_service, delete_crack_service, change_crack_visibility_service

router = APIRouter()

@router.post("/fetch-cracks")
def api_fetch_cracks(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to fetch cracks for a specific group."""
    group_id = data.get("group_id")
    
    return fetch_cracks_service(group_id, db)

@router.post("/add-crack")
def api_add_crack(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to add a new crack."""
    user_id = data.get("user_id")
    image_base64 = data.get("image_base64")
    
    return add_crack_service(user_id, image_base64, db)

@router.post("/delete-crack")
def api_delete_crack(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to delete a crack."""
    crack_id = data.get("crack_id")
    user_id = data.get("user_id")
    
    return delete_crack_service(crack_id, user_id, db)

@router.post("/change-crack-visibility")
def api_change_crack_visibility(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to change the visibility of a crack."""
    crack_id = data.get("crack_id")
    visibility = data.get("visibility")
    
    return change_crack_visibility_service(crack_id, visibility, db)