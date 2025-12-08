from datetime import datetime, timezone, timedelta
from app.models.otp import OTP
from app.models.user import User
from app.utils.otp import generate_otp, verify_otp
from app.utils.email import send_email
from app.templates.otp_template import otp_email_template, forgot_password_otp_template

OTP_EXPIRATION_MINUTES = 5

def send_email_otp(email: str, name: str, resend: bool, db):
    now = datetime.now(timezone.utc)

    if resend:
        # Delete existing OTPs for this email
        db.query(OTP).filter(OTP.email == email).delete()
        db.commit()

    # Check if user already has a VALID, UNEXPIRED OTP
    valid_otp = (
        db.query(OTP)
        .filter(OTP.email == email, OTP.expires_at > now)
        .order_by(OTP.created_at.desc())
        .first()
    )

    if valid_otp and not resend:
        # Ignore and return success but clarify nothing was sent
        return {"success": True, "message": "Valid OTP already exists. No new OTP sent."}

    # Generate a new OTP
    otp_code = generate_otp()

    # Save OTP to database
    new_otp = OTP(
        email=email,
        otp=otp_code,
        created_at=now,
        expires_at=now + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    )
    db.add(new_otp)
    db.commit()

    # Send OTP via email
    subject = "Your One-Time PIN (OTP)"
    content = otp_email_template(name, otp_code)
    send_email(email, subject, content)

    return {"success": True, "message": "OTP has been sent to your email"}

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

def send_forgot_password_otp(email: str, db):
    """Send OTP for forgot password functionality addressing to the first name."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "Email not found"}

    name = user.first_name
    otp = generate_otp()

    new_otp = OTP(
        email=email,
        otp=otp,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    )

    db.add(new_otp)
    db.commit()

    subject = "Your Password Reset OTP"
    content = forgot_password_otp_template(name, otp)
    send_email(email, subject, content)

    return {"success": True, "message": "OTP has been sent to your email"}