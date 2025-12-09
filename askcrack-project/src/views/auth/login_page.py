import flet as ft

from views.template import TemplatePage
from widgets.dialogs import ErrorDialog
from widgets.divider import or_divider
from widgets.inputs import AppTextField
from widgets.buttons import (
    BackButton,
    PrimaryButton,
    GoogleButton,
    CustomTextButton
)
from services.auth_service import login_user, forgot_password
from services.otp_service import send_forgot_password_otp, verify_otp
from utils.input_validator import validate_login, validate_email
from config import Config

class LoginPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
    
    def build(self) -> ft.View:
        """Build the login page UI"""
        # Back button
        self.appbar = ft.AppBar(
            leading=BackButton(
                on_click=lambda e: self.page.go("/")
            ),
            title=ft.Text("Login", size=18, weight="bold"),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.email_input = AppTextField(
            label="Email",
            value=self.page.client_storage.get("saved_email") or None,
            hint_text="Enter your email",
            prefix_icon=ft.Icons.PERSON,
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=lambda e: self.email_input.clear_error()
        )

        self.password_input = AppTextField(
            label="Password",
            hint_text="Enter your password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.password_input.clear_error()
        )

        # Buttons
        self.forgot_button = CustomTextButton(
            text="Forgot your Password?",
            on_tap=self.open_forgot_password_dialog,
        )

        # Login Button  
        self.login_button = PrimaryButton(
            text="Login",
            icon=ft.Icons.LOGIN,
            on_click=self.on_login,
        )

        self.google_login = GoogleButton(on_click=lambda e: print("Google"))

        # Main container content
        main_container = ft.Container(
            width=500,
            content=ft.ListView(
                padding=ft.padding.all(20),
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
                    ft.Divider(opacity=0),
                    self.email_input,
                    self.password_input,
                    self.forgot_button,
                    ft.Divider(height=1, opacity=0),
                    self.login_button,
                    or_divider(),
                    self.google_login,
                ]
            ),
            padding=ft.padding.only(top=30, bottom=0),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(top_left=30, top_right=30),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            expand=True
        )

        content = [
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Title outside container
                    ft.Column(height=20),  # spacer
                    ft.Container(
                        ft.Text("Cracktify", size=36, weight="bold"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(height=20),  # spacer
                    main_container,  # the login box
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)

    def on_login(self, e):
        """Handle login button click"""
        email = self.email_input.value
        password = self.password_input.value

        # Display error dialog if login fails
        error_dialog = ErrorDialog(
            title="Login Failed",
            content="Invalid email or password. Please try again.",
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
            ]
        )

        # Validate inputs
        is_valid, errors = validate_login(email, password)

        if is_valid:
            self.show_loading()
            self.page.run_task(self.user_login) # Perform login asynchronously

        else:
            # Display errors
            self.email_input.error_text = errors.get("email", "")
            self.password_input.error_text = errors.get("password", "")
            self.page.update()

    async def user_login(self):
        """Perform user login asynchronously"""
        email = self.email_input.value
        password = self.password_input.value

        response = await login_user(email, password)

        if response.get("success"):
            self.hide_loading()

            token = response.get("token")
            user = response.get("user")
            
            # Save token to client storage
            await self.page.client_storage.set_async("auth_token", token)
            await self.page.client_storage.set_async("user_info", user)

            self.page.go("/home")

        else:
            self.hide_loading()

            error_dialog = ErrorDialog(
                title=ft.Text("Login Failed"),
                content=ft.Text("Invalid email or password. Please try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
                ]
            )
            self.page.open(error_dialog)

    def open_forgot_password_dialog(self, e):
        """Open the forgot password dialog"""
        self.forgot_password_email_input = AppTextField(
            label="Email",
            hint_text="Enter your email",
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=lambda e: self.forgot_password_email_input.clear_error()
        )

        self.forgot_password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Forgot Password"),
            content=ft.Column(
                [
                    ft.Text("Enter your email address to reset your password."),
                    self.forgot_password_email_input
                ],
                height=150,
                spacing=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.forgot_password_dialog)),
                ft.TextButton("Submit", on_click=self.on_forgot_password_submit)
            ]
        )

        self.page.open(self.forgot_password_dialog)

    def on_forgot_password_submit(self, e):
        """Handle forgot password submission"""
        # Validate email
        is_valid, error = validate_email(self.forgot_password_email_input.value)
        if is_valid:
            self.page.close(self.forgot_password_dialog)
            self.show_loading()
            self.page.run_task(self.forgot_password_request)  # Perform forgot password request asynchronously
        else:
            self.forgot_password_email_input.error_text = error.get("email", "")
            self.page.update()


    async def forgot_password_request(self):
        """Sends forgot password OTP request asynchronously"""
        email = self.forgot_password_email_input.value

        response = await send_forgot_password_otp(email)

        self.otp_input = AppTextField(
            label="Enter OTP",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        if response.get("success"):
            self.page.close(self.forgot_password_dialog)
            self.hide_loading()

            self.otp_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Enter OTP"),
                content=ft.Column(
                    [
                        ft.Text("An OTP has been sent to your email. Please enter it below to reset your password."),
                        self.otp_input
                    ],
                    height=150,
                    spacing=10
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.otp_dialog)),
                    ft.TextButton("Verify OTP", on_click=self.on_verify_otp)
                ]
            )
            self.page.open(self.otp_dialog)

        else:
            self.hide_loading()

            error_dialog = ErrorDialog(
                title=ft.Text("Error"),
                content=ft.Text(response.get("message", "An error occurred. Please try again.")),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
                ]
            )
            self.page.open(error_dialog)

    def on_verify_otp(self, e):
        """Handle OTP verification"""
        self.entered_otp = self.otp_input.value

        self.page.close(self.otp_dialog)
        self.show_loading()
        self.page.run_task(self.verify_otp_request)  # Perform OTP verification asynchronously

    async def verify_otp_request(self):
        """Verifies the entered OTP asynchronously"""
        email = self.forgot_password_email_input.value
        entered_otp = self.entered_otp

        response = await verify_otp(email, entered_otp)

        if response.get("success"):
            self.hide_loading()
            await self.page.client_storage.set_async("reset_email", email)
            self.page.go("/change-password")

        else:
            self.hide_loading()

            error_dialog = ErrorDialog(
                title=ft.Text("Error"),
                content=ft.Text(response.get("message", "Invalid OTP. Please try again.")),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.open(self.otp_dialog))
                ]
            )
            self.page.open(error_dialog)

