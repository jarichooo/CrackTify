import asyncio
import flet as ft


async def toggle_theme(page, theme_button: ft.IconButton = None):
    """Toggles between light and dark themes."""
    new_theme = (
        ft.ThemeMode.DARK
        if page.theme_mode != ft.ThemeMode.DARK
        else ft.ThemeMode.LIGHT
    )  # Toggle to the opposite theme

    if theme_button:
        theme_button.icon = (
            # ft.Icons.DARK_MODE if new_theme == ft.ThemeMode.DARK else ft.Icons.LIGHT_MODE
            ft.Icons.LIGHT_MODE
            if new_theme == ft.ThemeMode.LIGHT
            else ft.Icons.DARK_MODE
        )  # Update the button icon to reflect the new theme

    page.theme_mode = new_theme

    await page.shared_preferences.set("theme_mode", new_theme.value)
    page.update()
