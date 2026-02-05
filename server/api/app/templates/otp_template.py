
def otp_email_template(name: str, otp: str) -> str:
    return f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color:#f4f6f8; padding:20px;">
            <div style="max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); overflow:hidden;">
                <div style="background-color:#007BFF; color:#ffffff; text-align:center; padding:30px 20px; font-size:24px; font-weight:bold;">
                    Verification Code
                </div>
                <div style="padding:30px 20px; color:#333333; line-height:1.6;">
                    <p>Hello {name},</p>
                    <p>Thank you for using our service. Your verification code is:</p>
                    <p style="text-align:center; font-size:28px; font-weight:bold; color:#007BFF;">{otp}</p>
                    <p>Enter this code in the app to verify your email address. This code will expire in 5 minutes.</p>
                </div>
                <div style="background-color:#f0f2f5; text-align:center; padding:20px; font-size:12px; color:#888888;">
                    &copy; 2025 Cracktify. All rights reserved.
                </div>
            </div>
        </div>
    """

def forgot_password_otp_template(name: str, otp: str) -> str:
    return f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color:#f4f6f8; padding:20px;">
            <div style="max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); overflow:hidden;">
                <div style="background-color:#28A745; color:#ffffff; text-align:center; padding:30px 20px; font-size:24px; font-weight:bold;">
                    Password Reset Code
                </div>
                <div style="padding:30px 20px; color:#333333; line-height:1.6;">
                    <p>Hello {name},</p>
                    <p>We received a request to reset your password. Your password reset code is:</p>
                    <p style="text-align:center; font-size:28px; font-weight:bold; color:#28A745;">{otp}</p>
                    <p>Enter this code in the app to reset your password. This code will expire in 5 minutes.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                </div>
                <div style="background-color:#f0f2f5; text-align:center; padding:20px; font-size:12px; color:#888888;">
                    &copy; 2025 Cracktify. All rights reserved.
                </div>
            </div>
        </div>
    """