import flet as ft
from .template import TemplatePage
from config import Config

class LoginPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Build the login page UI"""
        # Back button
        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Back",
                on_click=lambda e: self.page.go("/"),
            ),
            title=ft.Container(
                content=ft.Text("Login", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.email_input = ft.TextField(
            label="Email",
            hint_text="Enter your email",
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=ft.Colors.BLUE_ACCENT_100,
            prefix_icon=ft.Icons.PERSON,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.password_input = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            border_color=ft.Colors.BLUE_ACCENT_100,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        # Forgot password button
        self.forgot_button = ft.GestureDetector(
            content=ft.Text(
                "Forgot your Password?",
                text_align="center"
            ),
            on_tap=lambda _: print('hello world')
        )

        # Login button
        self.login_button = ft.FilledButton(
            "Login",
            icon=ft.Icons.LOGIN,
            width=self.dynamic_width(),
            height=50,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16))
        )

        # OR Divider
        or_divider = ft.Row(
            controls=[
                ft.Container(content=ft.Divider(), expand=True),
                ft.Text("Or", opacity=0.7),
                ft.Container(content=ft.Divider(), expand=True)
            ],
            width=self.dynamic_width(),
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Google login
        self.google_login = ft.FilledTonalButton(
            content=ft.Row(
                controls=[
                    ft.Image(src="Google_logo.png", width=20, height=20),
                    ft.Text("Sign in with Google", size=16, weight=ft.FontWeight.NORMAL)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=self.dynamic_width(),
            height=50
        )

        main_container = ft.Container(
            content=ft.ListView(
                expand=True,
                padding=ft.padding.all(20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Let's Sign You In", size=28, weight="bold"),
                            ft.Text("Welcome back, you've been missed!", size=14)
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(opacity=0),
                    self.email_input,
                    self.password_input,
                    # ft.Divider(height=1, opacity=0),
                    self.forgot_button,
                    ft.Divider(height=1, opacity=0),
                    self.login_button,
                    or_divider,
                    self.google_login
                ],
            ),
            padding=ft.padding.only(top=30, bottom=30),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            
        )

        # Combine all content
        content = [
            ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        ft.Text("Cracktify", size=36, weight="bold"),
                        alignment=ft.alignment.top_center
                    ),
                    main_container
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ]

        # Wrap with TemplatePage layout
        return self.layout(content, appbar=self.appbar)



