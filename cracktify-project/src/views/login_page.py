import asyncio

import flet as ft

from .template import TemplatePage

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
        )

        google_button = GoogleButton(
            text="Sign in with Google",
        )

        register_button = ft.Row(
            controls=[
                ft.Text("Don't have an account?", size=14),
                CustomTextButton(
                    text="Register Here",
                    on_tap=lambda: asyncio.create_task(self.page.push_route("/register")))
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
    
    def on_forgot_password_click(self, e):
        """Handles the forgot password button click event."""
        self.email_field = TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            expand=True
        )

        self.email_dialog = ft.AlertDialog(
            title=ft.Text("Forgot Password"),
            modal=True,
            content=ft.Column(
                height=130,
                spacing=10,
                controls=[
                    ft.Text("Please enter your email address to reset your password."),
                    self.email_field
                ]
            ),
            actions=[
                ft.TextButton(
                    content="Cancel",
                    on_click=lambda e: self.page.pop_dialog()
                ),
                ft.TextButton(
                    content="Send Reset Link",
                    on_click=self.send_reset_code
                )
            ],
        )

        self.page.show_dialog(self.email_dialog)

    def send_reset_code(self, e):
        self.page.pop_dialog()
        confirmation_dialog = ft.AlertDialog(
            title=ft.Text("Reset Code Sent"),
            content=ft.Text(f"A code to reset your password has been sent to {self.email_field.value}. Please check your email."),
            actions=[
                ft.TextButton(
                    content="Continue",
                    on_click=lambda: asyncio.create_task(self.page.push_route("/forgot-password"))
                )
            ],
        )
        self.page.show_dialog(confirmation_dialog)