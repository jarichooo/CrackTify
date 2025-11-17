import flet as ft
from .template import TemplatePage
from config import Config

class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)  # configure page automatically

    def build(self) -> ft.View:
        # --- Back button + title ---
        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self.page.go("/"),  # go back
            tooltip="Back"
        )

        title = ft.Text(
            "Create an account",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.LEFT,
        )

        header_row = ft.Row(
            controls=[back_button, title],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        # --- Google sign-in button ---
        google_register = ft.OutlinedButton(
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

        # --- OR Divider ---
        or_divider = ft.Row(
            controls=[
                ft.Container(content=ft.Divider(), expand=True),
                ft.Text("OR"),
                ft.Container(content=ft.Divider(), expand=True)
            ]
        )

        # --- Input fields ---
        email_input = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            width=450,
        )

        username_input = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON,
            width=450,
        )

        password_input = ft.TextField(
            label="Password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=450,
        )

        # --- Next button ---
        next_button = ft.ElevatedButton(
            "Next",
            width=450,
            height=48,
        )

        # --- Page content ---
        content = [
            ft.Container(
                content=header_row,
                padding=ft.padding.only(top=40)
            ),
            google_register,
            or_divider,
            email_input,
            username_input,
            password_input,
            next_button,
        ]

        # --- Wrap with template layout ---
        return self.layout("Register", content)
