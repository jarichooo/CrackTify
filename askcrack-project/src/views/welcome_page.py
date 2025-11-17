import flet as ft
from .template import TemplatePage

class WelcomePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)  # configure page automatically

    def build(self) -> ft.View:
        # --- Main content ---
        content = [
            ft.Text("Welcome!", size=30, weight="bold"),
            ft.ElevatedButton("Login", on_click=lambda _: self.page.go("/login")),
            ft.TextButton("Create an account", on_click=lambda _: self.page.go("/register")),
        ]

        # --- Wrap with template layout ---
        return self.layout("Welcome", content)
