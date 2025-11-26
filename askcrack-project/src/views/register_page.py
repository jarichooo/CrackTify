import flet as ft

from .template import TemplatePage
from widgets.divider import or_divider
from widgets.inputs import AppTextField
from widgets.buttons import (
    BackButton,
    PrimaryButton,
    GoogleButton,
    CustomTextButton
)
from config import Config

class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Build the registration page UI"""

        # Back button and header
        self.appbar = ft.AppBar(
            leading=BackButton(
                on_click=lambda e: self.page.go("/")
            ),
            title=ft.Container(
                content=ft.Text("Register", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.full_name = AppTextField(
            label="Full Name",
            hint_text="Enter your full name",
        )

        self.email_input = AppTextField(
            label="Email",
            hint_text="Enter your email",
        )

        self.password_input = AppTextField(
            label="Password",
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
        )

        self.confirm_password_input = AppTextField(
            label="Confirm Password",
            hint_text="Re-enter your password",
            password=True,
            can_reveal_password=True,
        )

        # Register button
        self.continue_button = PrimaryButton(
            text="Continue",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self.on_continue,
        )

        self.agree_checkbox = ft.Checkbox(
            label="By creating an account, you agree to our \nTerms and Condition",
            label_style=ft.TextStyle(size=14),
            
        )

        # Google Register Button
        self.google_register = GoogleButton(
            text="Sign up with Google",
            on_click=lambda e: print("Google register clicked")  # Placeholder action
        )

        # Main content container
        main_container = ft.Container(
            content= ft.ListView(
                # expand=True,
                padding=ft.padding.all(20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Welcome to Cracktify", size=28, weight="bold"),
                            ft.Text("Create your account to start detecting cracks", size=14)
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, opacity=0),

                    self.google_register,
                    or_divider(),

                    self.full_name,
                    self.email_input,
                    self.password_input,
                    self.confirm_password_input,
                    self.agree_checkbox,

                    self.continue_button
                ]
            ),
            padding=ft.padding.only(top=10, bottom=10),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            expand=True
        )

        # Page layout
        content = [
            ft.Column(
                expand=True,
                controls=[
                    main_container,   # starts immediately below back button
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)
    
    def on_continue(self, e):
        self.page.go("/otp")


class OTPPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        email_address = "sample_email@gmail.com"

        # Back button and header
        self.appbar = ft.AppBar(
            leading=BackButton(
                on_click=lambda e: self.page.go("/register")
            ),
            title=ft.Container(
                content=ft.Text("Enter OTP", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # OTP input field
        self.otp_input = AppTextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
        )

        # Submit button
        self.submit_button = PrimaryButton(
            text="Submit",
            icon=ft.Icons.CHECK,
            on_click=self.on_submit,
        )

        # Resend OTP row
        self.resend_otp = ft.Row(
            controls=[
                ft.Text("Didn't receive the code?", size=14),
                CustomTextButton(
                    text="Resend OTP",
                    on_tap=lambda e: print("Resend OTP clicked")
                )
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER
        )

        main_container = ft.Container(
            content= ft.ListView(
                expand=True,
                padding=20,
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Verify your email", size=28, weight="bold"),
                            ft.Text("A 6-digit authentication code has been sent to", size=14),
                            ft.Text(email_address, size=14, color=ft.Colors.BLUE_ACCENT_100)
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(opacity=0),
                    self.otp_input,
                    self.submit_button,
                    self.resend_otp
                ]
            ),
            padding=ft.padding.only(top=50, bottom=50),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            expand=True
        )

        content = [
            ft.Column(
                expand=True,
                controls=[
                    main_container
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)
    
    def on_submit(self, e):
        self.page.go("/home")
