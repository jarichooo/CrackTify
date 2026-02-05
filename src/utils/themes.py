import flet as ft

def toggle_theme(page: ft.Page, button: ft.IconButton = None):
    """Toggles between light and dark themes."""
    if button.icon == ft.Icons.DARK_MODE:
        page.theme_mode = ft.ThemeMode.LIGHT
        button.icon = ft.Icons.LIGHT_MODE

    else:
        page.theme_mode = ft.ThemeMode.DARK
        button.icon = ft.Icons.DARK_MODE

    page.update()