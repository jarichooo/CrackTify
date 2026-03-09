import asyncio
import flet as ft
from views.template import TemplatePage
from widgets.inputs import TextField
from widgets.buttons import BackButton, PrimaryButton


class ForgotPasswordPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Builds the forgot password Page layout."""
        back_button = BackButton(
            on_click=lambda: asyncio.create_task(self.page.push_route("/login"))
        )

        self.reset_code_field = TextField(
            label="Reset Code",
            hint_text="Enter the reset code sent to your email",
        )

        self.new_password_field = TextField(
            label="New Password", password=True, can_reveal_password=True
        )

        self.confirm_password_field = TextField(
            label="Confirm New Password", password=True, can_reveal_password=True
        )

        reset_button = PrimaryButton(
            text="Reset Password",
        )

        main_container = self.main_container(
            content=ft.ListView(
                padding=ft.Padding.only(left=20, right=20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(height=10),  # Spacer
                    ft.Container(back_button, alignment=ft.Alignment.TOP_LEFT),
                    ft.Column(height=20),  # Spacer
                    ft.Container(
                        ft.Text("Cracktify", size=32, weight="bold"),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(height=30),  # Spacer
                    self.reset_code_field,
                    self.new_password_field,
                    self.confirm_password_field,
                    reset_button,
                ],
            )
        )

        return self.layout(
            route="/forgot-password",
            controls=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(height=50),  # Spacer
                    ft.Container(
                        ft.Text("Cracktify", size=32, weight="bold"),
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.only(top=50, bottom=50),
                    ),
                    ft.Column(height=20),  # Spacer
                    main_container,
                ],
            ),
        )
