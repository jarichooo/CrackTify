import flet as ft

from .template import TemplatePage
from widgets.buttons import PrimaryButton, SecondaryButton

class WelcomePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self):
        """Build the welcome page UI"""
        content = [
            ft.Stack(
                expand=True,  # fills the screen
                controls=[
                    # Centered title
                    ft.Container(
                        ft.Text("Cracktify", size=36, weight="bold"),
                        alignment=ft.alignment.center
                    ),

                    # Buttons pinned to bottom
                    ft.Container(
                        ft.Column(
                            controls=[
                                PrimaryButton(
                                    text="Create an account",
                                    width=self.dynamic_width(),
                                    on_click=lambda _: self.page.go("/register")
                                ),
                                SecondaryButton(
                                    text="Login",
                                    width=self.dynamic_width(),
                                    on_click=lambda _: self.page.go("/login")
                                ),
                                ft.Text(
                                    "By continuing, you agree to our Terms of Service and Privacy Policy.",
                                    size=10,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(top=20, bottom=30),
                        left=20,
                        right=20,
                        bottom=10
                    ),
                ],

            )
        ]

        return self.layout(content)
