import flet as ft
from .template import TemplatePage
from config import Config

class LoginPage(TemplatePage):
    def __init__(self, page: ft.Page):
        # Call parent constructor to configure page
        super().__init__(page)

    def build(self):
        # --- Title ---
        title = ft.Text(
            value=Config.APP_TITLE,
            size=48,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        subtitle = ft.Text(
            value="A crack detection system for mobile",
            size=14,
            opacity=0.7,
            text_align=ft.TextAlign.CENTER,
        )

        # --- Inputs ---
        username_input = ft.TextField(
            label="Username",
            hint_text="Enter your username or email",
            prefix_icon=ft.Icons.PERSON,
            autofocus=True,
            width=450,
        )

        password_input = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=450,
        )

        forgot_button = ft.TextButton(
            "Forgot Password?",
            style=ft.ButtonStyle(color=ft.Colors.BLUE),
        )

        login_button = ft.ElevatedButton(
            text="Login",
            icon=ft.Icons.LOGIN,
            width=450,
            height=48,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16))
        )

        or_divider = ft.Row(
            controls=[
                ft.Container(content=ft.Divider(), expand=True),
                ft.Text("OR", opacity=0.7),
                ft.Container(content=ft.Divider(), expand=True)
            ]
        )

        google_login = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Image(src="Google_logo.png", width=20, height=20),
                    ft.Text("Sign in with Google", size=16)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=450,
            height=48,
        )

        register_row = ft.Row(
            controls=[
                ft.Text("Don't have an account?"),
                ft.TextButton(
                    "Register Here",
                    on_click=lambda e: self.page.go("/register")
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # --- Use Template Layout ---
        content = [
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [title, subtitle],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=ft.padding.only(top=80),
                    ),
                    username_input,
                    password_input,
                    ft.Row([forgot_button], alignment=ft.MainAxisAlignment.END, width=450),
                    login_button,
                    or_divider,
                    google_login,
                ],
            ),
            ft.Container(content=register_row, padding=20)
        ]

        # Return layout using the TemplatePage wrapper
        return self.layout("Login", content)
