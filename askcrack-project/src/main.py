import flet as ft
from views import WelcomePage, LoginPage, RegisterPage


def main(page: ft.Page):
    page.title = "Flet App with Views"
    page.window_width = 400
    page.window_height = 700

    # --- Routing ---
    def route_change(route):
        page.views.clear()

        if page.route == "/" or page.route == "":
            page.views.append(WelcomePage(page).build())

        elif page.route == "/login":
            page.views.append(LoginPage(page).build())

        elif page.route == "/register":
            page.views.append(RegisterPage(page).build())

        else:
            page.views.append(ft.View("/", controls=[ft.Text("Page not found")]))
        
        page.update()

    # --- Handle back button / view pop ---
    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
        else:
            page.window_close()  # or just ignore if first view

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Go to initial route
    page.go(page.route)


ft.app(target=main)
