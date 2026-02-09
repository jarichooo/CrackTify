from typing import List
from pathlib import Path

import flet as ft

class HomeSection:
    def __init__(self, page: ft.Page, user):
        self.page = page
        self.user = user

    def build(self) -> List[ft.Control]:
        """Builds the about Page layout."""
        # self.recent_
        self.body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            content=ft.Text(
                value="Welcome to the Home Page!",
                size=24,
                weight="bold",
                color=ft.Colors.PRIMARY
            )
        )

        return [
            self.body
        ]