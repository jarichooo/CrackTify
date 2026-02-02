import asyncio
import flet as ft
from views.login_page import LoginPage
from views.register_page import RegisterPage
from views.forgot_password_page import ForgotPasswordPage
from views.main_page import MainPage

from views.not_found import NotFoundPage


def main(page: ft.Page):
    page.title = "Cracktify"

    def route_change():
        page.views.clear()
        page.views.append(MainPage(page).build())
        # page.views.append(NotFoundPage(page).build())  

        # if page.route == "/" or page.route == "/login":
            # page.views.append(LoginPage(page).build())
        if page.route == "/home" or page.route == "/":
            page.views.append(MainPage(page).build())
        
        elif page.route == "/login":
            page.views.append(LoginPage(page).build())

        elif page.route == "/register":
            page.views.append(RegisterPage(page).build())

        elif page.route == "/forgot-password":
            page.views.append(ForgotPasswordPage(page).build())

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

    route_change()

if __name__ == "__main__":
    ft.run(main, upload_dir="uploads")
