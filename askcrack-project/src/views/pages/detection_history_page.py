import flet as ft
from typing import List

class DetectionHistoryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:
        self.content = [
            ft.Text("Detection History", style="headlineMedium"),
            ft.Text("View the history of detections made by the system.", style="bodyMedium"),
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]
