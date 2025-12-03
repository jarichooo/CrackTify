import flet as ft
from typing import List

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Control]:
        self.content = [
            ft.Text("Welcome to the Home Page!", style="headlineMedium"),
            ft.Text("This is where the main content will go.", style="bodyMedium"),
            ft.ElevatedButton("Click Me", on_click=self.on_button_click)
        ]
        container = ft.Column(controls=self.content, alignment=ft.MainAxisAlignment.CENTER)
        
        return [container]

    def on_button_click(self, e: ft.ControlEvent):
        self.page.snackbar = ft.Snackbar(ft.Text("Button clicked!"))
        self.page.snackbar.open = True
        self.page.update()
