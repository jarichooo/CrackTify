import asyncio

import flet as ft
from .template import TemplatePage

class NotFoundPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        return self.layout(
            route="/not_found",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Column(
                controls=[
                    ft.Text(
                        value="404 - Page Not Found",
                        size=30,
                        weight="bold",
                        color=ft.Colors.ERROR
                    ),
                    ft.Text(
                        value="The page you are looking for does not exist.",
                        size=16,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Button(
                        content="Go to Home",
                        on_click=lambda: asyncio.create_task(
                            self.page.push_route("/home")
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )