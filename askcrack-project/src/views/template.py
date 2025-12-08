import flet as ft
from config import Config

class TemplatePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.loading_overlay = ft.Container(
            visible=False,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
            alignment=ft.alignment.center,
            content=ft.Container(
                width=120,
                height=120,
                # bgcolor=ft.Colors.WHITE,
                border_radius=12,
                alignment=ft.alignment.center,
                content=ft.ProgressRing(color=ft.Colors.INVERSE_PRIMARY),
            ),
        )

        self.configure_page()
        
        if hasattr(self.page, "on_pop"):
            self.page.on_pop = self.on_back

    def on_back(self, e):
        # 'e' exists only on mobile, ignore on desktop
        handled = False

        if self.search_active:
            self.toggle_search(None)
            handled = True

        elif self.action_buttons.visible:
            self.open_detect_menu(None)
            handled = True

        elif hasattr(self, "profile_overlay") and self.profile_overlay in self.page.controls:
            self.close_profile(None)
            handled = True

        elif len(self.page.views) > 1:
            self.page.go_back()
            handled = True

        if handled and hasattr(e, "prevent_default"):
            e.prevent_default = True


    def configure_page(self):
        """Page/window configuration"""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 0
        self.page.spacing = 0

        # self.page.platform = ft.PagePlatform.ANDROID
        self.is_light = True if self.page.theme_mode == ft.ThemeMode.LIGHT else False

        # self.page.window.width = Config.APP_WIDTH
        # self.page.window.height = Config.APP_HEIGHT

        # self.page.window.full_screen = True

        self.page.vertical_alignment = ft.CrossAxisAlignment.START
        self.page.horizontal_alignment = ft.MainAxisAlignment.CENTER

        self.page.overlay.append(self.loading_overlay)
        self.page.window.maximized = True

    def dynamic_width(self, width_ratio=0.9):
        """Return width based on page size for responsive controls"""
        return self.page.window.width * width_ratio
    
    def show_loading(self):
        self.loading_overlay.visible = True
        self.page.update()

    def hide_loading(self):
        self.loading_overlay.visible = False
        self.page.update()

    def layout(
        self,
        content: list[ft.Control] | None = None,
        drawer: ft.NavigationDrawer | None = None,
        appbar: ft.AppBar | None = None,
        floating_action_button: ft.FloatingActionButton | None = None,
        padding: ft.Padding | None = ft.padding.only(),

    ) -> ft.View:
        """Return a View with content directly."""

        return ft.View(
            route=self.page.route,
            padding=padding,
            appbar=appbar,
            drawer=drawer,
            controls=content,
            floating_action_button=floating_action_button,
        )
