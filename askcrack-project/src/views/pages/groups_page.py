import flet as ft
from typing import List

class GroupsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Groups", style="headlineMedium"),
            ft.Text("Manage and view your groups here.", style="bodyMedium"),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]