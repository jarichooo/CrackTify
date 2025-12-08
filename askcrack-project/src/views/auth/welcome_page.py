from pathlib import Path
import flet as ft
from views.template import TemplatePage
from widgets.buttons import PrimaryButton, SecondaryButton

class WelcomePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        # self.image_path = Path(__file__).parent.parent.parent.parent / "src" / "assets" / "icon.png"
        # print(self.image_path)

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
                        height=450,
                    ),

                    # # Image (Logo)
                    # ft.Container(
                    #     width=400,
                    #     height=200,
                    #     border_radius=16,
                    #     alignment=ft.alignment.center,
                    #     content=ft.Image(
                    #         error_content=ft.Text("Image not found"),
                    #         src=str(self.image_path),
                    #         fit=ft.ImageFit.CONTAIN,
                    #     )
                    # ),

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
                                    width=500,
                                    on_click=lambda _: self.page.go("/register")
                                ),
                                SecondaryButton(
                                    text="Login",
                                    width=500,
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
