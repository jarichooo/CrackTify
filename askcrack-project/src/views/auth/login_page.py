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
from services.auth_service import login_user
from utils.input_validator import validate_login
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
            on_tap=lambda e: print("Forgot clicked")
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
