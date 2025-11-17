import flet as ft
from config import Config

class TemplatePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.configure_page()

    def configure_page(self):
        """Page/window configuration"""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 100
        self.page.spacing = 30

        # Window properties
        self.page.window.min_width = Config.MIN_WIDTH
        self.page.window.max_width = Config.MAX_WIDTH
        self.page.window.height = Config.MAX_HEIGHT
        self.page.window.width = Config.MAX_WIDTH
        self.page.window.min_height = Config.MIN_HEIGHT
        self.page.window.max_height = Config.MAX_HEIGHT

        self.page.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        self.page.window.alignment = ft.alignment.center

    def layout(self, title: str, content: list[ft.Control]):
        """Base layout wrapper for all pages."""
        return ft.View(
            route=self.page.route,
            controls=[
                ft.Text(title, size=28, weight="bold"),
                ft.Divider(),
                ft.Column(content, spacing=15)
            ]
        )
