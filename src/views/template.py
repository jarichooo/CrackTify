import asyncio
import json
import flet as ft
from config import Config


class TemplatePage:
    def __init__(self, page: ft.Page):
        self.page = page

        # Loading overlay
        self.loading_text = ft.Text(
            "",
            text_align=ft.TextAlign.CENTER,
        )

        self.loading_overlay = ft.Container(
            visible=False,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Column(height=10),  # Spacer
                    self.loading_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # Add overlay immediately
        self.page.overlay.append(self.loading_overlay)

        self.saved_theme: str | None = None
        self.saved_user: dict = {}
        self.auth_token: str | None = None

        self.page.run_task(self.configure_page)
        self.page.run_task(self.load_shared_preferences)

    async def configure_page(self):
        self.page.title = Config.APP_TITLE

        self.saved_theme = await self.page.shared_preferences.get("theme_mode")
        self.saved_theme_color = await self.page.shared_preferences.get("theme_color")

        if self.saved_theme:
            self.page.theme_mode = ft.ThemeMode(self.saved_theme)
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        self.is_light = self.page.theme_mode == ft.ThemeMode.LIGHT

        if self.saved_theme_color:
            self.page.theme = ft.Theme(
                color_scheme_seed=ft.Colors(self.saved_theme_color)
            )

        if self.loading_overlay not in self.page.overlay:
            self.page.overlay.append(self.loading_overlay)

        self.page.window.height = 820
        self.page.window.width = 430

    def horizontal_divider(
        self, with_or: bool = False, height: int | None = None, opacity: float = 1.0
    ) -> ft.Row | ft.Divider:
        """Create a horizontal divider with optional 'OR' text in the CENTER."""
        if with_or:
            return ft.Row(
                controls=[
                    ft.Container(content=ft.Divider(), expand=True),
                    ft.Text("Or", opacity=0.7),
                    ft.Container(content=ft.Divider(), expand=True),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        else:
            return ft.Divider(height=height, opacity=opacity)

    def show_loading(self, loading_msg="Loading..."):
        self.loading_text.value = loading_msg
        self.loading_overlay.visible = True
        self.page.update()

    def hide_loading(self):
        """Hide the loading overlay."""
        self.loading_overlay.visible = False
        self.loading_text.value = ""
        self.page.update()

    async def load_shared_preferences(self):
        raw_saved_user = await self.page.shared_preferences.get("saved_user")
        self.saved_user = json.loads(raw_saved_user) if raw_saved_user else {}
        self.auth_token = await self.page.shared_preferences.get("auth_token")

    def main_container(self, content: ft.ListView) -> ft.Container:
        """Create the main container for authentication forms."""
        return ft.Container(
            width=500,
            padding=ft.Padding.only(top=30, bottom=0),
            alignment=ft.Alignment.CENTER,
            border_radius=ft.BorderRadius.only(top_left=30, top_right=30),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            expand=True,
            content=content,
        )

    def layout(
        self,
        route: str = "/",
        navigation_bar: ft.NavigationBar | None = None,
        controls: ft.Control = None,
        padding: ft.Padding | None = 0,
        spacing: int = 10,
        **kwargs,
    ) -> ft.View:
        """Creates a standard layout for pages."""
        return ft.View(
            route=route,
            controls=controls,
            padding=padding,
            spacing=spacing,
            navigation_bar=navigation_bar,
            **kwargs,
        )
