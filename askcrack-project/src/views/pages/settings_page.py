import flet as ft
from typing import List

class SettingsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Settings", style="headlineMedium"),
            ft.Text("Adjust your application settings here.", style="bodyMedium"),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)

        return [container]
