import flet as ft
from typing import List

class ReportsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Reports Page Coming Soon!", size=20, weight="bold"),
            ft.Text("This section will display user reports and related analytics.", size=14),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]
