import asyncio
import json
import os
import sys

from model import user

# Ensure vendor packages are in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import flet as ft

from widgets.dialogs import AlertDialog
from views.auth.login_page import LoginPage
from views.main_page import MainPage

from views.not_found import NotFoundPage
from model.user import User

from services.api_client import verify_connection


async def main(page: ft.Page):
    # page.shared_preferences.clear()
    """Main function to initialize the Flet application."""
    page.title = "Cracktify"  # Set the window title

    def pop_return():
        page.pop_dialog()
        sys.exit(0)

    async def safe_get(key: str, retries: int = 3, delay: float = 0.5):
        """Retries shared_preferences.get on timeout to handle Android platform channel not being ready."""
        for attempt in range(retries):
            try:
                return await page.shared_preferences.get(key)
            except RuntimeError:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
        return None  # give up after retries

    # Verify API connection before proceeding
    # Show a loading overlay while checking the connection
    page.overlay.append(
        ft.Container(
            visible=True,
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Image(src="splash_android.png", width=230, height=230),
                            ft.Text("Cracktify", size=28, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=-30,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(height=10),  # Spacer
                    ft.ProgressRing(),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
    )
    page.update()
    connection_ok = await verify_connection()
    if not connection_ok:
        page.overlay.pop()  # Remove the loading overlay
        conn_error_dialog = AlertDialog(
            title="Connection Error",
            content="Unable to connect to the API server. Please check your internet connection and try again.",
            actions=[ft.TextButton("OK", on_click=lambda e: pop_return())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(conn_error_dialog)
        return

    page.overlay.pop()  # Remove the loading overlay

    async def route_change():
        # Clear existing views and push the new view based on the current route
        # Show a loading overlay while changing routes
        page.overlay.append(
            ft.Container(
                visible=True,
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(),
                        ft.Column(height=10),  # Spacer
                        ft.Text(
                            "Loading...",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            )
        )
        page.update()

        raw_user = await safe_get("user")
        user = json.loads(raw_user) if raw_user else {}
        User.from_dict(user)  # Update the User model with the loaded data

        page.views.clear()
        page.overlay.pop()  # Remove the loading overlay

        if page.route == "/home" or page.route == "/":
            main_page = MainPage(page)
            page.views.append(main_page.build())

            if user.get("is_engineer") and not user.get("verified"):
                from views.verify_engineer import VerifyEngineerPage
                page.views.append(VerifyEngineerPage(page).build())

        elif page.route == "/login":
            login_page = LoginPage(page)
            page.views.append(login_page.build())

        else:
            page.views.append(NotFoundPage(page).build())

        page.update()

    async def view_pop(e):
        # When a view is popped, check if there are any views left.
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    # Attach the route change and view pop handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Check for auth token in shared preferences to determine initial route
    auth_token = await safe_get("auth_token")

    if auth_token:
        page.route = "/home"
    
    else:
        page.route = "/login"

    await route_change()  # Manually trigger route change to load the initial view

if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")