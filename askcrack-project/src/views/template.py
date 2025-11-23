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
        self.page.padding = 0
        self.page.spacing = 0

        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT

        self.page.vertical_alignment = ft.CrossAxisAlignment.START
        self.page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    def dynamic_width(self, width_ratio=0.9):
        """Return width based on page size for responsive controls"""
        return self.page.window.width * width_ratio
    
    def layout(
        self,
        content: list[ft.Control],
        drawer: ft.NavigationDrawer = None,
        appbar: ft.AppBar = None,
        floating_action_button: ft.FloatingActionButton = None

    ) -> ft.View:
        """Return a View with content directly."""

        return ft.View(
            padding=ft.padding.only(top=30, bottom=30),
            route=self.page.route,
            appbar=appbar,
            drawer=drawer,
            controls=content,
            floating_action_button=floating_action_button
        )
