import asyncio
import flet as ft
from config import Config

class TemplatePage:
    def __init__(self, page: ft.Page):
        self.page = page

        # Loading overlay
        self.loading_overlay = ft.Container(
            visible=False,
            expand=True,    
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
            content=ft.Container(
                width=120,
                height=120,
                border_radius=12,
                alignment=ft.Alignment.CENTER,
                content=ft.ProgressRing(color=ft.Colors.INVERSE_PRIMARY)
            )
        )
        
        self.configure_page()
    
    def configure_page(self):
        """Configure common page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM

        self.is_light = True if self.page.theme_mode == ft.ThemeMode.LIGHT else False
    
        self.page.overlay.append(self.loading_overlay)
        self.page.window.maximized = True

    def horizontal_divider(
        self, 
        with_or: bool = False, 
        height: int | None = None, 
        opacity: float = 1.0
    ) -> ft.Row | ft.Divider:
        """Create a horizontal divider with optional 'OR' text in the CENTER."""
        if with_or:
            return ft.Row(
                controls=[
                    ft.Container(content=ft.Divider(), expand=True),
                    ft.Text("Or", opacity=0.7),
                    ft.Container(content=ft.Divider(), expand=True)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            return ft.Divider(height=height, opacity=opacity)
    
    def show_loading(self):
        """Show the loading overlay."""
        self.loading_overlay.visible = True
        self.page.update()

    def hide_loading(self):
        """Hide the loading overlay."""
        self.loading_overlay.visible = False
        self.page.update()

    def main_container(self, content: ft.ListView) -> ft.Container:
        """Create the main container for authentication forms."""
        return ft.Container(
            width=500,
            padding=ft.Padding.only(top=30, bottom=0),
            alignment=ft.Alignment.CENTER,
            border_radius=ft.BorderRadius.only(top_left=30, top_right=30),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            expand=True,
            content=content
        )

    def layout(
        self, route: str = "/", 
        navigation_bar: ft.NavigationBar | None = None,
        controls: ft.Control = None,
        padding: ft.Padding | None = 0,
        spacing: int = 10,
        **kwargs
    ) -> ft.View:
        """Creates a standard layout for pages."""
        return ft.View(route=route, controls=controls, padding=padding, spacing=spacing, navigation_bar=navigation_bar, **kwargs)