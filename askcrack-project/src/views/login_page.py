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
# from services.database import get_connection
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
            title=ft.Container(
                content=ft.Text("Login", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.email_input = AppTextField(
            label="Email",
            hint_text="Enter your email",
            prefix_icon=ft.Icons.PERSON,
            keyboard_type=ft.KeyboardType.EMAIL,
        )

        self.password_input = AppTextField(
            label="Password",
            hint_text="Enter your password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
        )

        # Forgot password button
        self.forgot_button = CustomTextButton(
            text="Forgot your Password?",
            on_tap=lambda e: print("Forgot Password clicked")
        )

        # Login button
        self.login_button = PrimaryButton(
            text="Login",
            icon=ft.Icons.LOGIN,
            # on_click=self.login,
        )

        # Google login
        self.google_login = GoogleButton(
            on_click=lambda e: print("Google login clicked")  # Placeholder action
        )

        main_container = ft.Container(
            content=ft.ListView(
                expand=True,
                padding=ft.padding.all(20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Let's Sign You In", size=28, weight="bold"),
                            ft.Text("Welcome back, you've been missed!", size=14)
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(opacity=0),
                    self.email_input,
                    self.password_input,
                    # ft.Divider(height=1, opacity=0),
                    self.forgot_button,
                    ft.Divider(height=1, opacity=0),
                    self.login_button,
                    or_divider(),
                    self.google_login
                ],
            ),
            padding=ft.padding.only(top=30, bottom=30),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            
        )

        # Combine all content
        content = [
            ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        ft.Text("Cracktify", size=36, weight="bold"),
                        alignment=ft.alignment.top_center
                    ),
                    main_container
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ]

        # Wrap with TemplatePage layout
        return self.layout(content, appbar=self.appbar)
    
    # def login(self, e):
    #     """Handle login button click"""
    #     email = self.email_input.value
    #     password = self.password_input.value

    #     if not email or not password:
    #         self.page.snack_bar = ft.SnackBar(
    #             ft.Text("Please enter both email and password."),
    #             bgcolor=ft.Colors.RED
    #         )
    #         self.page.snack_bar.open = True
    #         self.page.update()
    #         return

    #     if self.authenticate_user(email, password):
    #         self.page.go("/home")
    #     else:
    #         self.page.snack_bar = ft.SnackBar(
    #             ft.Text("Invalid email or password."),
    #             bgcolor=ft.Colors.RED
    #         )
    #         self.page.snack_bar.open = True
    #         self.page.update()


    # def authenticate_user(self, email: str, password: str) -> bool:
    #     """Authenticate user with given email and password"""
    #     connection = get_connection()
    #     cursor = connection.cursor()

    #     cursor.execute(
    #         "SELECT password_hash FROM users WHERE email = ?", (email,)
    #     )
    #     result = cursor.fetchone()

    #     connection.close()

    #     if result:
    #         stored_password_hash = result[0]
    #         # Here you would normally hash the provided password and compare
    #         return stored_password_hash == password  # Simplified for example
    #     return False