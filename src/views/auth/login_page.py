import asyncio
import json

import flet as ft


from config import Config
from services.auth_service import login_user
from utils.input_validation import validate_login, validate_email
from views.auth.register_page import RegisterPage

from views.template import TemplatePage

from widgets.inputs import TextField
from widgets.buttons import PrimaryButton, SecondaryButton, GoogleButton, CustomTextButton, BackButton

class LoginPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Builds the authentication Page layout."""
        self.email_field = TextField(
            label="Email",
            value="",
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL
        )

        self.password_field = TextField(
            label="Password",
            value="",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True
        )

        forgot_button = CustomTextButton(
            text="Forgot Password?",
            on_tap=self.on_forgot_password_click
        )

        login_button = PrimaryButton(
            text="Login",
            icon=ft.Icons.LOGIN,
            on_click=self.on_login_click
        )

        google_button = GoogleButton(
            text="Sign in with Google",
            on_click=lambda _: self.page.run_task(self.handle_google_sign_in)
        )

        register_button = ft.Row(
            controls=[
                ft.Text("Don't have an account?", size=14),
                CustomTextButton(
                    text="Register Here",
                    on_tap=lambda: self.page.views.append(RegisterPage(self.page).build())
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        main_container = self.main_container(
            content=ft.ListView(
                padding=ft.Padding.only(left=20, right=20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Let’s Sign You In", size=28, weight="bold"),
                            ft.Text("Welcome back, you've been missed!", size=14),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.horizontal_divider(opacity=0),
                    self.email_field,
                    self.password_field,
                    forgot_button,
                    self.horizontal_divider(height=1, opacity=0),
                    login_button,
                    self.horizontal_divider(with_or=True),
                    google_button,
                    register_button,
                    self.horizontal_divider(height=5, opacity=0),
                ]
            ),
        )

        return self.layout(
            route="/",
            controls=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(height=50),  # Spacer
                    ft.Container(
                        ft.Text("Cracktify", size=32, weight="bold"),
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.only(top=50, bottom=50)
                    ),
                    ft.Column(height=20),  # Spacer
                    main_container
                ],
            ),
        )
    
    async def handle_google_sign_in(self):
        """Handles the Google sign-in button click event."""
        try:
            from flet.auth import OAuthProvider

            provider = OAuthProvider(
                client_id=Config.GOOGLE_CLIENT_ID,
                client_secret=Config.GOOGLE_CLIENT_SECRET,
                redirect_url=Config.GOOGLE_REDIRECT_URI
            )

            await self.page.login(provider)
            self.page.on_login = self.on_google_login_success
            
        except Exception as e:
            error_dialog = ft.AlertDialog(
                title=ft.Text("Google Sign-In Failed"),
                content=ft.Text(str(e)),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())
                ]
            )
            self.page.show_dialog(error_dialog)
            return

        # Checks if email is in database after successful Google sign-in
        # If not, it will create a new account for the user and then navigate to the home page

    def on_google_login_success(self):
        """Handles successful Google login and navigates to the home page."""
        # Here you would typically check if the user's email exists in your database
        # If it doesn't, create a new user account with the information from Google
        # Then navigate to the home page

        # For demonstration, we'll just navigate to the home page directly
        self.page.push_route("/home")

    def on_login_click(self, e):
        """Handles the login button click event."""
        email = self.email_field.value
        password = self.password_field.value

        # Validate inputs
        is_valid, errors = validate_login(email, password)

        if is_valid:
            self.show_loading()
            self.page.run_task(self.user_login, email, password) # Perform login asynchronously

        else:
            # Display errors
            self.email_field.error = errors.get("email")
            self.password_field.error = errors.get("password")
            self.page.update()

    async def user_login(self, email, password):
        """Perform user login asynchronously"""
        response = await login_user(email, password)
        self.hide_loading()

        if response.get("success"):
            # If login is successful, save the token and navigate to the home page
            token = response.get("token")
            user = response.get("user")
            
            await self.page.shared_preferences.set("auth_token", token)
            await self.page.shared_preferences.set("user", json.dumps(user))

            await self.page.push_route("/home")

        else:
            # If login fails, show an error dialog with the message from the response
            error_dialog = ft.AlertDialog(
                title=ft.Text("Login Failed"),
                content=ft.Text(response.get("message", "An unknown error occurred.")),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())
                ]
            )
            self.page.show_dialog(error_dialog)

    def on_forgot_password_click(self, e):
        """Handles the forgot password button click event."""
        self.fp_email_field = TextField(
            label="Email",
            value=self.email_field.value,
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            autofocus=True,
            on_focus=self.validate_fp_email,
            on_change=self.validate_fp_email,
            suffix_icon=ft.IconButton(
                icon=ft.Icons.SEND,
                on_click=self.send_reset_code,
                tooltip="Send OTP",
            )
        )

        self.fp_otp_field = TextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            prefix_icon=ft.Icons.FIBER_PIN,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            disabled=True,
            on_change=self.enable_send_button
        )

        self.email_dialog = ft.AlertDialog(
            title=ft.Text("Forgot Password"),
            modal=True,
            content=ft.Column(
                height=200,
                spacing=10,
                controls=[
                    ft.Text("Enter your email to receive an OTP to reset your password.", size=14),
                    self.fp_email_field,
                    self.fp_otp_field
                ]
            ),
            actions=[
                ft.TextButton(
                    content="Cancel",
                    on_click=lambda e: self.page.pop_dialog()
                ),
                ft.TextButton(
                    content="Send Reset Link",
                    disabled=True,
                    on_click=self.verify_reset_otp
                )
            ],
        )

        self.page.show_dialog(self.email_dialog)
    
    def validate_fp_email(self, e):
        """Validates the email input in the forgot password dialog."""
        is_valid, error = validate_email(self.fp_email_field.value)
        self.fp_email_field.error = None  # Clear previous error

        if not is_valid:
            self.fp_email_field.suffix_icon.visible = False
            self.fp_email_field.helper = error["email"]
            self.page.update()

        else:
            self.fp_email_field.suffix_icon.visible = True
            self.fp_email_field.helper = None
            self.page.update()

    async def send_reset_code(self, e):
        """"Handles sending the password reset code to the user's email."""
        from services.otp_service import send_forgot_password_otp

        email = self.fp_email_field.value.strip() # Get the email from the forgot password email field and strip any leading/trailing whitespace

        # Hide the send button and show a loading indicator while sending the OTP
        self.fp_email_field.suffix_icon.visible = False
        self.fp_email_field.helper = "Sending OTP..."
        self.page.update()

        response = await send_forgot_password_otp(email) # Call the service function to send the forgot password OTP to the user's email

        if response.get("success"):
            # If the OTP was sent successfully, enable the OTP input field and show a success message
            self.fp_otp_field.disabled = False
            self.fp_email_field.disabled = True
            self.fp_email_field.suffix_icon.visible = False

            self.fp_email_field.helper = "An OTP has been sent to your email address."
            self.fp_email_field.helper_style = ft.TextStyle(color=ft.Colors.GREEN_500)

            self.page.update()
        else:
            # If there was an error sending the OTP, show an error message and re-enable the send button
            self.fp_email_field.error = response.get("message", "Failed to send OTP. Please try again.")
            self.page.update()

    def enable_send_button(self, e):
        """Enables the send reset link button when the OTP input field has a valid 6-digit code."""
        otp_value = self.fp_otp_field.value.strip()
        self.fp_otp_field.error = None  # Clear previous error

        if len(otp_value) == 6 and otp_value.isdigit():
            self.email_dialog.actions[1].disabled = False
        else:
            self.email_dialog.actions[1].disabled = True

        self.page.update()

    async def verify_reset_otp(self, e):
        from services.otp_service import verify_otp
    
        email = self.fp_email_field.value.strip()
        otp = self.fp_otp_field.value.strip()


        self.fp_otp_field.helper = "Verifying OTP..."
        self.page.update()
        response = await verify_otp(email, otp)

        if response.get("success"):
            # Opens the reset password dialog if the OTP is verified successfully
            self.new_password_field = TextField(
                label="New Password",
                value="",
                prefix_icon=ft.Icons.LOCK,
                password=True,
                can_reveal_password=True
            )

            self.confirm_new_password_field = TextField(
                label="Confirm New Password",
                value="",
                prefix_icon=ft.Icons.LOCK,
                password=True,
                can_reveal_password=True
            )

            self.page.pop_dialog()
            reset_password_dialog = ft.AlertDialog(
                title=ft.Text("Reset Password"),
                modal=True,
                height=250,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("Enter your new password below.", size=14),
                        self.new_password_field,
                        self.confirm_new_password_field
                    ]
                ),
                actions=[
                    ft.TextButton(
                        content="Cancel",
                        on_click=lambda e: self.page.pop_dialog()
                    ),
                    ft.TextButton(
                        content="Reset Password",
                        on_click=self.reset_password
                    )
                ],
            )
            self.page.show_dialog(reset_password_dialog)

        else:
            # Show error message
            self.fp_otp_field.helper = None
            self.fp_otp_field.error = response.get("message", "Invalid OTP. Please try again.")
            self.page.update()

    async def reset_password(self, e):
        """Handles the password reset process after OTP verification."""
        from services.auth_service import forgot_password
        from utils.input_validation import validate_password_change

        new_password = self.new_password_field.value
        confirm_new_password = self.confirm_new_password_field.value

        # Validate the new password and confirm password fields
        is_valid, error = validate_password_change(
            current_password=None, 
            new_password=new_password, 
            confirm_password=confirm_new_password
        )

        if not is_valid:
            self.new_password_field.error = error.get("new_password")
            self.confirm_new_password_field.error = error.get("confirm_password")
            self.page.update()
            return

        email = self.fp_email_field.value.strip()

        self.confirm_new_password_field.helper = "Resetting password..."
        self.page.update()

        response = await forgot_password(email, new_password)

        if response.get("success"):
            self.page.pop_dialog()
            success_dialog = ft.AlertDialog(
                title=ft.Text("Password Reset Successful"),
                content=ft.Text("Your password has been reset successfully. You can now log in with your new password."),
                actions=[
                    ft.TextButton(
                        content="OK",
                        on_click=lambda e: self.page.pop_dialog()
                    )
                ]
            )
            self.page.show_dialog(success_dialog)
        else:
            self.hide_loading()
            error_dialog = ft.AlertDialog(
                title=ft.Text("Password Reset Failed"),
                content=ft.Text(response.get("message", "Failed to reset password. Please try again.")),
                actions=[
                    ft.TextButton(
                        content="OK",
                        on_click=lambda e: self.page.pop_dialog()
                    )
                ]
            )
            self.page.show_dialog(error_dialog)
   