import flet as ft
from .template import TemplatePage
from widgets.buttons import PrimaryButton, SecondaryButton

class WelcomePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self):
        return self.layout([
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[

                    # Title
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "Cracktify",
                            size=36,
                            weight="bold",
                        ),
                        height=self.page.window.height * 0.4,  # keeps it centered
                    ),

                    # Buttons
                    ft.Container(
                        padding=ft.padding.only(
                            left=20,
                            right=20,
                            bottom=20,
                        ),
                        content=ft.Column(
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ],
                        ),
                    ),
                ],
            )
        ]
    )
