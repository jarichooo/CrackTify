import asyncio

import flet as ft

from .template import TemplatePage

from widgets.inputs import TextField
from widgets.buttons import PrimaryButton, SecondaryButton, GoogleButton, CustomTextButton, BackButton

class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        
    def build(self) -> ft.View:
        """Builds the registration Page layout."""
        back_button = BackButton(
            on_click=lambda: self.page.views.pop()
        )
        
        appbar = ft.AppBar(
            leading=back_button,
        )

        google_button = GoogleButton(
            text="Sign up with Google",
        )

        self.first_name_field = TextField(
            label="First Name",
            hint_text="Enter your first name",
            autofocus=True,
            expand=1
        )

        self.last_name_field = TextField(
            label="Last Name",
            hint_text="Enter your last name",
            expand=1
        )

        self.email_field = TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
        )

        self.password_field = TextField(
            label="Password",
            password=True,
            can_reveal_password=True
        )

        self.confirm_password_field = TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True
        )

        continue_button = PrimaryButton(
            text="Continue",
        )

        main_container = self.main_container(
            content=ft.ListView(
                padding=ft.Padding.only(left=20, right=20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Let’s Register", size=28, weight="bold"),
                            ft.Text("Create a new account", size=14),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    
                    self.horizontal_divider(height=1, opacity=0),
                    google_button,
                    self.horizontal_divider(with_or=True),

                    ft.Row(
                        spacing=10,
                        controls=[
                            self.first_name_field,
                            self.last_name_field
                        ],
                    ),

                    self.email_field,
                    self.password_field,
                    self.confirm_password_field,
                    self.horizontal_divider(height=1, opacity=0),
                    continue_button,
                ]
            ),
        )

        return self.layout(
            route="/register",
            controls=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[
                    ft.Column(height=10),  # Spacer
                    ft.Container(
                        back_button,
                        alignment=ft.Alignment.TOP_LEFT
                    ),
                    ft.Column(height=20),  # Spacer
                    ft.Container(
                        ft.Text("Cracktify", size=32, weight="bold"),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(height=20),  # Spacer
                    main_container
                ],
            ),
        )
