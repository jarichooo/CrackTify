import flet as ft

def toggle_theme(e, page: ft.Page, theme_button) -> None:
    """Toggle between light and dark themes"""
    current_theme = page.theme_mode

    if current_theme == ft.ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.DARK
        theme_button.icon = ft.Icons.DARK_MODE

    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        theme_button.icon = ft.Icons.LIGHT_MODE
        
    page.update()