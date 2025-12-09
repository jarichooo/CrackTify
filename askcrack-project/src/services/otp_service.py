from typing import Dict, Any
from .api_client import post_request

async def send_otp(email: str, name: str, resend: bool = False) -> Dict[str, Any]:
    return await post_request(
        "/otp/send-otp",
        {
            "email": email,
            "name": name,
            "resend": resend
        }
    )

async def verify_otp(email: str, entered_otp: str) -> Dict[str, Any]:
    return await post_request(
        "/otp/verify-otp",
        {
            "email": email,
            "entered_otp": entered_otp
        }
    )

async def send_forgot_password_otp(email: str)-> Dict[str, Any]:
    return await post_request(
        "/otp/send-forgot-password-otp",
        {
            "email": email,
        }
    )

