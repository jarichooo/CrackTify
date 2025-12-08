import flet as ft
from views.main_page import MainPage
from views.auth.login_page import LoginPage
from views.auth.register_page import RegisterPage
from views.auth.otp_page import OTPPage
from views.auth.welcome_page import WelcomePage
from views.auth.new_password_page import ForgotPasswordPage

def main(page: ft.Page):
    """Main function to run the app"""
    def login_check():
        """Check for existing login token"""
        token = page.client_storage.get("auth_token")
        if token:
            page.go("/home")

    # Routing
    def route_change(route):
        """Handle route changes"""
        page.views.clear()

        if page.route == "/" or page.route == "":
            page.views.append(WelcomePage(page).build())

        elif page.route == "/login":
            page.views.append(LoginPage(page).build())

        elif page.route == "/change-password":
            page.views.append(ForgotPasswordPage(page).build())

        elif page.route == "/register":
            page.views.append(RegisterPage(page).build())

        elif page.route == "/otp":
            page.views.append(OTPPage(page).build())

        elif page.route == "/home":
            page.views.append(MainPage(page).build())

        elif page.route == "/logout":
            page.client_storage.remove("auth_token")
            page.client_storage.remove("user_info")
            page.go("/login")

        else:
            page.views.append(ft.View("/", controls=[ft.Text("Page not found")]))
        
        page.update()

    # Handle back button / view pop
    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
        else:
            page.window_close()  # or just ignore if first view

    login_check() # Check for existing login on app start

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Go to initial route
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
