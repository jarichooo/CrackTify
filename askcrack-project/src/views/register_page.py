import flet as ft
from .template import TemplatePage

class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Build the registration page UI"""

        # Back button and header
        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Back",
                on_click=lambda e: self.page.go("/"),
            ),
            title=ft.Container(
                content=ft.Text("Register", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.full_name = ft.TextField(
            label="Full Name",
            # prefix_icon=ft.Icons.PERSON,
            hint_text="Enter your full name",
            border_color=ft.Colors.BLUE_ACCENT_100,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.email_input = ft.TextField(
            label="Email",
            hint_text="Enter your email",
            # prefix_icon=ft.Icons.EMAIL,
            border_color=ft.Colors.BLUE_ACCENT_100,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.username_input = ft.TextField(
            label="Username",
            hint_text="Choose a username",
            # prefix_icon=ft.Icons.PERSON,
            border_color=ft.Colors.BLUE_ACCENT_100,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.password_input = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            border_color=ft.Colors.BLUE_ACCENT_100,
            # prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.confirm_password_input = ft.TextField(
            label="Confirm Password",
            hint_text="Re-enter your password",
            border_color=ft.Colors.BLUE_ACCENT_100,
            # prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        # Register button
        self.continue_button = ft.FilledButton(
            "Continue",
            width=self.dynamic_width(),
            height=50,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=self.on_continue
        )

        # OR Divider
        or_divider = ft.Row(
            controls=[
                ft.Container(content=ft.Divider(), expand=True),
                ft.Text("Or", opacity=0.7),
                ft.Container(content=ft.Divider(), expand=True),
            ],
            width=self.dynamic_width(),
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.agree_checkbox = ft.Checkbox(
            label="By creating an account, you agree to our \nTerms and Condition",
            label_style=ft.TextStyle(size=14),
            
        )

        # Google Register Button
        self.google_register = ft.FilledTonalButton(
            content=ft.Row(
                controls=[
                    ft.Image(src="Google_logo.png", width=20, height=20),
                    ft.Text("Sign up with Google", size=16)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=self.dynamic_width(),
            height=50
        )

        # Main content container
        self.main_container = ft.Container(
            content= ft.ListView(
                # expand=True,
                padding=ft.padding.all(20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Welcome to Cracktify", size=28, weight="bold"),
                            ft.Text("Create your account to start detecting cracks", size=14)
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, opacity=0),

                    self.google_register,
                    or_divider,

                    self.full_name,
                    self.email_input,
                    self.password_input,
                    self.confirm_password_input,
                    self.agree_checkbox,

                    self.continue_button
                ]
            ),
            padding=ft.padding.only(top=10, bottom=10),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            expand=True
        )


        # Page layout
        content = [
            ft.Column(
                expand=True,
                controls=[
                    self.main_container,   # starts immediately below back button
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)
    
    def on_continue(self, e):
        self.page.go("/otp")


class OTPPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        email_address = "sample_email@gmail.com"

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Back",
                on_click=lambda e: self.page.go("/register"),
            ),
            title=ft.Container(
                content=ft.Text("Enter OTP", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        self.otp_input = ft.TextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            border_color=ft.Colors.BLUE_ACCENT_100,
            width=self.dynamic_width(),
            border_radius=ft.border_radius.all(10)
        )

        self.submit_button = ft.FilledButton(
            "Submit",
            width=self.dynamic_width(),
            height=50,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=self.on_submit
        )

        self.resend_otp = ft.Row(
            controls=[
                ft.Text("Didn't receive the code?", size=14),
                ft.GestureDetector(
                    content=ft.Text(" Resend", size=14, color=ft.Colors.BLUE_ACCENT_100, weight="bold"),
                    on_tap=lambda e: print("Resend OTP clicked")
                )
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.main_container = ft.Container(
            content= ft.ListView(
                expand=True,
                padding=20,
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Verify your email", size=28, weight="bold"),
                            ft.Text("A 6-digit authentication code has been sent to", size=14),
                            ft.Text(email_address, size=14, color=ft.Colors.BLUE_ACCENT_100)
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(opacity=0),
                    self.otp_input,
                    self.submit_button,
                    self.resend_otp
                ]
            ),
            padding=ft.padding.only(top=50, bottom=50),
            alignment=ft.alignment.center,
            border_radius=30,
            bgcolor=ft.Colors.BLUE_50 if self.is_light else ft.Colors.BLACK87,
            expand=True
        )

        content = [
            ft.Column(
                expand=True,
                controls=[
                    self.main_container
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)
    
    def on_submit(self, e):
        self.page.go("/home")
