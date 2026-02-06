
import asyncio
import os
import sys

# Ensure vendor packages are in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import flet as ft

from views.auth.login_page import LoginPage
from views.main_page import MainPage

from views.not_found import NotFoundPage

from services.api_client import verify_connection

async def main(page: ft.Page):
    """Main function to initialize the Flet application."""

    connection_ok = await verify_connection()
    if not connection_ok:
        page.add(
            ft.AlertDialog(
                title=ft.Text("Connection Error"),
                content=ft.Text("Unable to connect to the API server. Please check your internet connection and try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: page.window_destroy())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )
        page.update()
        return

    def window_event(e: ft.WindowEvent):
        # Intercept the window close event to show a confirmation dialog
        if e.type == ft.WindowEventType.CLOSE:
            page.show_dialog(confirm_dialog)
            page.update()

    page.title = "Cracktify" # Set the window title
    page.window.prevent_close = True # Prevent the window from closing immediately 
    page.window.on_event = window_event # Attach the window event handler

    async def handle_yes_click(e: ft.Event[ft.Button]):
        # Close the confirmation dialog and then close the window
        await page.window.destroy()

    def handle_no_click(e: ft.Event[ft.OutlinedButton]):
        # Close the confirmation dialog without closing the window
        page.pop_dialog()
        page.update()

    # Create the confirmation dialog
    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to exit this app?"),
        actions=[
            ft.Button(content="Yes", on_click=handle_yes_click),
            ft.OutlinedButton(content="No", on_click=handle_no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def route_change():
        # Clear existing views and push the new view based on the current route
        page.views.clear()
        if page.route == "/home" or page.route == "/":
            page.views.append(MainPage(page).build())

        elif page.route == "/login":
            page.views.append(LoginPage(page).build())

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

    route_change() # Manually trigger route change to load the initial view

if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")


