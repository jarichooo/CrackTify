from typing import Dict, Any
from .api_client import post_request


async def send_otp(email: str, name: str, resend: bool = False) -> Dict[str, Any]:
    try:
        response = await post_request(
            "/otp/send-otp", {"email_address": email, "name": name, "resend": resend}
        )
        return response
    except Exception as ex:
        return {"success": False, "message": str(ex)}


async def verify_otp(email: str, entered_otp: str) -> Dict[str, Any]:
    try:
        return await post_request(
            "/otp/verify-otp", {"email_address": email, "entered_otp": entered_otp}
        )
    except Exception as ex:
        print(f"Error in verify_otp: {ex}")
        return {"success": False, "message": str(ex)}


async def send_forgot_password_otp(email: str) -> Dict[str, Any]:
    try:
        return await post_request(
            "/otp/send-forgot-password-otp",
            {
                "email_address": email,
            },
        )
    except Exception as ex:
        return {"success": False, "message": str(ex)}
