import flet as ft

from .template import TemplatePage

class MorePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        saved_theme_mode = self.page.shared_preferences.get("theme_mode")
        if saved_theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif saved_theme_mode == "system":
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        saved_theme_color = self.page.shared_preferences.get("theme_color")
        if saved_theme_color:
            color_map = {
                "red": ft.Colors.RED,
                "blue": ft.Colors.BLUE,
                "green": ft.Colors.GREEN,
                "yellow": ft.Colors.YELLOW,
            }
            chosen = color_map.get(saved_theme_color, ft.Colors.BLUE)
            self.page.theme = ft.Theme(color_scheme_seed=chosen)

        self.new_email = None  # To store new email during change process

    def build(self) -> ft.View:
        app_bar = ft.AppBar(
            automatically_imply_leading=True,
        )

        self.avatar_image = ft.Container(
            width=100,
            height=100,
            border_radius=50,
            bgcolor=ft.Colors.GREY_300,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=self.on_avatar_click,
            content=ft.Image(
                src="https://www.gravatar.com/avatar/?d=mp&s=200",
                fit=ft.BoxFit.COVER,
            )
        )

        return self.layout(
            route="/more",
            appbar=app_bar,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                
                self.avatar_image,
            ]
        )
    
    async def on_avatar_click(self, e):
        """Handle avatar image click to pick a new image file."""
        self.file_picker = ft.FilePicker()

        files = await self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])
        if not files:
            return
        
        file = files[0]
        self.picked_file = file

        # Update avatar image
        self.avatar_image.content.src = file.path