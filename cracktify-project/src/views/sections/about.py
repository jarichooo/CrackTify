from typing import List
from pathlib import Path

import flet as ft

class AboutSection:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> List[ft.Control]:
        """Builds the about Page layout."""
        self.body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            content=ft.Text(
                value="Welcome to the About Page!",
                size=24,
                weight="bold",
                color=ft.Colors.PRIMARY
            )
        )

        return [
            self.body
        ]