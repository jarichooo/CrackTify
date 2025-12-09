from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.otp_service import send_email_otp, send_forgot_password_otp, verify_entered_otp

router = APIRouter()

@router.post("/send-otp")
def api_send_otp(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    name = data.get("name")
    resend = data.get("resend", False)

    return send_email_otp(email, name, resend=resend, db=db)

@router.post("/verify-otp")
def api_verify_otp(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    otp = data.get("entered_otp")
    
    return verify_entered_otp(email, otp, db)

@router.post("/send-forgot-password-otp")
def api_send_forgot_password_otp(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")

    return send_forgot_password_otp(email, db)