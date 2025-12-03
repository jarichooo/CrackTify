import flet as ft
from typing import List

class HelpPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Help & Support", style="headlineMedium"),
            ft.Text("Find answers to common questions and get support.", style="bodyMedium"),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]

