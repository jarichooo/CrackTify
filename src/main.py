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
from views.admin_page import AdminPage          # ← new

from views.not_found import NotFoundPage
from model.user import User

from services.api_client import verify_connection
from services.profile_service import get_current_user
from services.ws_client import WSClient


async def main(page: ft.Page):
    """Main function to initialize the Flet application."""
    page.title = "Cracktify"

    # Initialize WebSocket client for real-time notifications
    ws = WSClient()

    def on_login_success(user_id: str, notification_handler):
        if not user_id:
            return
        ws.start(user_id, lambda data: asyncio.create_task(
            notification_handler(data)
        ))

    def on_logout():
        ws.stop()

    def pop_return():
        page.pop_dialog()
        sys.exit(0)

    async def safe_get(key: str, retries: int = 3, delay: float = 0.5):
        """Retries shared_preferences.get on timeout."""
        for attempt in range(retries):
            try:
                return await page.shared_preferences.get(key)
            except RuntimeError:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
        return None

    async def safe_set(key: str, value: str, retries: int = 3, delay: float = 0.5):
        """Retries shared_preferences.set on timeout."""
        for attempt in range(retries):
            try:
                await page.shared_preferences.set(key, value)
                return True
            except RuntimeError:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
        return False

    # ── Splash / connection check ─────────────────────────────────────
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
                    ft.Column(height=10),
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
        page.overlay.pop()
        conn_error_dialog = AlertDialog(
            title="Connection Error",
            content="Unable to connect to the API server. Please check your internet connection and try again.",
            actions=[ft.TextButton("OK", on_click=lambda e: pop_return())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(conn_error_dialog)
        return

    page.overlay.pop()

    # ── Route handler ─────────────────────────────────────────────────
    async def route_change():
        # Loading overlay while switching routes
        page.overlay.append(
            ft.Container(
                visible=True,
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(),
                        ft.Column(height=10),
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

        # ── Determine session type ────────────────────────────────────
        is_admin_flag = await safe_get("is_admin")       # "true" | "" | None
        auth_token    = await safe_get("auth_token")
        is_admin      = is_admin_flag == "true" and bool(auth_token)

        raw_user = await safe_get("user")
        user: dict = {}
        if raw_user:
            try:
                parsed = json.loads(raw_user)
                if isinstance(parsed, dict):
                    user = parsed
            except Exception:
                user = {}

        # Only refresh the User model for non-admin sessions
        if not is_admin:
            try:
                u_resp = await get_current_user(str(user.get("id", 0)))
                if u_resp.get("success"):
                    user = u_resp.get("user", {})
                    await safe_set("user", json.dumps(user))
                User.from_dict(user)
            except Exception as e:
                print(f"Error updating User model: {e}")

        page.views.clear()
        page.overlay.pop()

        # ── /admin ───────────────────────────────────────────────────
        if page.route == "/admin":
            if not is_admin:
                # Safety guard: redirect to login if session is not admin
                await page.push_route("/login")
                return
            admin_page = AdminPage(page)
            page.views.append(admin_page.build())

        # ── /home or / ───────────────────────────────────────────────
        elif page.route == "/home" or page.route == "/":
            main_page = MainPage(page)
            page.views.append(main_page.build())

            if user.get("id"):
                on_login_success(
                    user.get("id"),
                    main_page.notification_page.handle_notification,
                )

            if user.get("is_engineer") and not user.get("verified"):
                from views.verify_engineer import VerifyEngineerPage
                page.views.append(VerifyEngineerPage(page).build())

        # ── /login ───────────────────────────────────────────────────
        elif page.route == "/login":
            on_logout()
            login_page = LoginPage(page)
            page.views.append(login_page.build())

        # ── 404 ──────────────────────────────────────────────────────
        else:
            page.views.append(NotFoundPage(page).build())

        page.update()

    async def view_pop(e):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ── Initial route decision ────────────────────────────────────────
    auth_token    = await safe_get("auth_token")
    is_admin_flag = await safe_get("is_admin")
    current_user  = await safe_get("user")

    if auth_token and is_admin_flag == "true":
        page.route = "/admin"
    elif auth_token and current_user:
        page.route = "/home"
    else:
        page.route = "/login"

    await route_change()


if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")