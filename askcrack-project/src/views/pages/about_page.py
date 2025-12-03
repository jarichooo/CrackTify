import flet as ft
from typing import List

class AboutPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("About Us", style="headlineMedium"),
            ft.Text("This application is designed to help users find answers to their questions.", style="bodyMedium"),

        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]