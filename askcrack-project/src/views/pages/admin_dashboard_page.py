import flet as ft
from typing import List

class AdminDashboardPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Admin Dashboard", style="headlineMedium"),
            ft.Text("Manage users, view statistics, and configure settings.", style="bodyMedium"),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]