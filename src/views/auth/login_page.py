import asyncio
import json

import flet as ft


from config import Config
from services.auth_service import login_user
from utils.input_validation import validate_login
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
        from flet.auth.providers import GoogleOAuthProvider

        provider = GoogleOAuthProvider(
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            redirect_url=Config.GOOGLE_REDIRECT_URI
        )

        await self.page.login(provider)

        # Checks if email is in database after successful Google sign-in
        # If not, it will create a new account for the user and then navigate to the home page
        self.page.on_login = self.on_google_login_success

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
                    on_click=lambda _: asyncio.create_task(self.page.push_route("/forgot-password"))
                )
            ],
        )
        self.page.show_dialog(confirmation_dialog)