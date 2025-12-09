from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.crack_service import delete_crack_from_group_service, fetch_cracks_service, add_crack_service

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
    probability = data.get("probability")
    severity = data.get("severity")
    
    return add_crack_service(user_id, image_base64, probability, severity, db)

@router.post("/delete-crack-from-group")
def api_delete_crack_from_group(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to delete a crack from a specific group."""
    crack_id = data.get("crack_id")
    group_id = data.get("group_id")
    
    return delete_crack_from_group_service(crack_id, group_id, db)
