import asyncio
import json
import os
import sys

# Ensure vendor packages are in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import flet as ft

from widgets.dialogs import AlertDialog
from views.auth.login_page import LoginPage
from views.main_page import MainPage
from views.more_page import MorePage

from views.not_found import NotFoundPage

from services.api_client import verify_connection
from services.profile_service import get_current_user


async def main(page: ft.Page):
    # page.shared_preferences.clear()
    """Main function to initialize the Flet application."""
    page.title = "Cracktify"  # Set the window title

    def pop_return():
        page.pop_dialog()
        sys.exit(0)

    # Verify API connection before proceeding
    connection_ok = await verify_connection()
    if not connection_ok:
        conn_error_dialog = AlertDialog(
            title="Connection Error",
            content="Unable to connect to the API server. Please check your internet connection and try again.",
            actions=[ft.TextButton("OK", on_click=lambda e: pop_return())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(conn_error_dialog)
        return

    async def route_change():
        # Clear existing views and push the new view based on the current route
        try:
            raw_user = await page.shared_preferences.get("user")
            user = json.loads(raw_user) if raw_user else {}
        except RuntimeError:
            error_dialog = AlertDialog(
                title="Runtime Error",
                content="An error occurred while loading user data. Please restart the application.",
                actions=[ft.TextButton("OK", on_click=lambda e: pop_return())],
            )
            page.show_dialog(error_dialog)
            return

        page.views.clear()
        if page.route == "/home" or page.route == "/":
            main_page = MainPage(page, user)
            page.views.append(main_page.build())

        elif page.route == "/login":
            login_page = LoginPage(page)
            page.views.append(login_page.build())

        elif page.route == "/more":
            more_page = MorePage(page, user)
            page.views.append(more_page.build())

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
    auth_token = await page.shared_preferences.get("auth_token")

    if auth_token:
        page.route = "/home"
    else:
        page.route = "/login"

    await route_change()  # Manually trigger route change to load the initial view


if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")
