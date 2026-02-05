
import asyncio
import os
import sys

# Ensure vendor packages are in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import flet as ft

from views.login_page import LoginPage
from views.register_page import RegisterPage
from views.forgot_password_page import ForgotPasswordPage
from views.main_page import MainPage

from views.not_found import NotFoundPage

async def main(page: ft.Page):
    page.title = "Cracktify"

    auth_token = await page.shared_preferences.get("auth_token")

    def route_change():
        page.views.clear()

        if page.route == "/home" or page.route == "/":
            page.views.append(MainPage(page).build())
        elif page.route == "/login":
            page.views.append(LoginPage(page).build())

        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.go_async(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if auth_token:
        page.route = "/home"
    else:
        page.route = "/login"

    route_change()

if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")


