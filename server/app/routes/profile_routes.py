from ast import Dict
import io
from typing import Any
from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import update_profile, verify_user_password, download_data, delete_account

router = APIRouter()

@router.post("/update/{user_id}")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    profile_data = data.get("profile_data", {})
    new_password = data.get("new_password")

    return update_profile(profile_data, new_password, db)

@router.post("/verify_password/{user_id}")
def api_verify_user_password(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    old_password = data.get("old_password")

    return verify_user_password(user_id, old_password, db)

@router.get("/download_data/{user_id}")
def api_download_data(user_id: int, db: Session = Depends(get_db)):
    # download_response = download_data(user_id, db)
    # if not download_response["success"]:
    #     return download_response
    
    # with open(f"user_{user_id}_data.pdf", "rb") as pdf_file:
    #     pdf_content = pdf_file.read()

    # return FileResponse(
    #     path=f"user_{user_id}_data.pdf",
    #     filename=f"user_{user_id}_data.pdf",
    #     media_type="application/pdf",
    #     headers={
    #         "Content-Disposition": f"attachment; filename=user_{user_id}_data.pdf"
    #     }
    # )
    pdf_bytes = download_data(user_id, db)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=user_{user_id}.pdf"}
    )

@router.post("/delete_account/{user_id}")
def api_delete_account(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    password = data.get("password")

    return delete_account(user_id, password, db)