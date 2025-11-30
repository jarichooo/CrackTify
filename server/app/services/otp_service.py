from datetime import datetime, timezone, timedelta
from app.models.otp import OTP
from app.utils.otp import generate_otp, verify_otp
from app.utils.email import send_email
from app.templates.otp_template import otp_email_template

OTP_EXPIRATION_MINUTES = 5
OTP_RESEND_COOLDOWN_SEC = 30

def send_email_otp(email: str, name: str, db):
    now = datetime.now(timezone.utc)

    if not email:
        return {"success": False, "error": "Missing email"}

    # Check if user already has a VALID, UNEXPIRED OTP
    valid_otp = (
        db.query(OTP)
        .filter(OTP.email == email, OTP.expires_at > now)
        .order_by(OTP.created_at.desc())
        .first()
    )

    if valid_otp:
        # Ignore and return success but clarify nothing was sent
        return {"success": True, "message": "Valid OTP already exists. No new OTP sent."}

    # Generate new OTP
    otp_code = generate_otp()

    # Save OTP in DB
    new_otp = OTP(email=email, otp=otp_code)

    db.add(new_otp)
    db.commit()

    # Send Email
    html = otp_email_template(name, otp_code)
    send_email(email, "Your OTP Code", html)

    return {"success": True, "message": "OTP sent successfully"}


def verify_entered_otp(email: str, entered_otp: str, db):
    now = datetime.now(timezone.utc)

    # Get the latest OTP for this email
    last_otp = db.query(OTP).filter(OTP.email == email).order_by(OTP.created_at.desc()).first()

    if not verify_otp(last_otp, entered_otp, now):
        return {"success": False, "message": "Invalid OTP"}

    # Optional: delete the OTP after successful verification
    db.delete(last_otp)
    db.commit()

    return {"success": True, "message": "Email has been verified"}
