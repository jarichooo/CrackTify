import flet as ft
import asyncio

from .template import TemplatePage
from widgets.buttons import (
    BackButton,
    PrimaryButton,
    GoogleButton,
    CustomTextButton
)
from widgets.divider import or_divider
from widgets.inputs import AppTextField
from services.otp_service import send_otp, verify_otp
from utils.input_validator import validate_registration

from config import Config


class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.saved_first_name = self.page.client_storage.get("register_first_name") or None
        self.saved_last_name = self.page.client_storage.get("register_last_name") or None
        self.saved_email = self.page.client_storage.get("register_email") or None
        self.saved_password = self.page.client_storage.get("register_password") or None
        self.saved_confirm_pw = self.page.client_storage.get("register_confirm_pw") or None
        self.saved_terms = self.page.client_storage.get("register_terms") or None

    def build(self) -> ft.View:
        """Build the registration page UI"""

        # Back button and header
        self.appbar = ft.AppBar(
            leading=BackButton(
                on_click=lambda e: self.page.go("/")
            ),
            title=ft.Container(
                content=ft.Text("Register", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # Inputs
        self.first_name = AppTextField(
            label="First Name",
            hint_text="Enter your first name",
            expand=1,
            on_change=lambda e: self.first_name.clear_error()
        )

        self.last_name = AppTextField(
            label="Last Name",
            hint_text="Enter your last name",
            expand=1,
            on_change=lambda e: self.last_name.clear_error()
        )

        self.email_input = AppTextField(
            value=self.saved_email,
            label="Email",
            hint_text="Enter your email",
            on_change=lambda e: self.email_input.clear_error()
        )

        self.password_input = AppTextField(
            value=self.saved_password,
            label="Password",
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.password_input.clear_error()
        )

        self.confirm_password_input = AppTextField(
            value=self.saved_confirm_pw,
            label="Confirm Password",
            hint_text="Re-enter your password",
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.confirm_password_input.clear_error()
        )

        # Register button
        self.continue_button = PrimaryButton(
            text="Continue",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self.on_continue,
        )

        # Checkbox
        self.agree_checkbox = ft.Checkbox(
            value=self.saved_terms,
            label="By creating an account, you agree to our \nTerms and Condition",
            label_style=ft.TextStyle(size=14),
            on_change=lambda e: self.agree_checkbox.update()
        )

        # Google Register Button
        self.google_register = GoogleButton(
            text="Sign up with Google",
            on_click=lambda e: print("Google register clicked")  # Placeholder action
        )

        # Main content container
        main_container = ft.Container(
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
                    or_divider(),

                    ft.Row(
                        spacing=5,
                        controls=[
                            self.first_name,
                            self.last_name
                        ]
                    ),
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
                    main_container,   # starts immediately below back button
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)

    def on_continue(self, e):
        """Handle continue button click"""
        first_name = self.first_name.value
        last_name = self.last_name.value
        email = self.email_input.value
        password = self.password_input.value
        confirm_password = self.confirm_password_input.value
        agree_terms = self.agree_checkbox.value

        # Call the utils function
        is_valid, errors = validate_registration(first_name, last_name, email, password, confirm_password)

        # Update input error texts
        self.first_name.error_text = errors.get("first_name")
        self.last_name.error_text = errors.get("last_name")
        self.email_input.error_text = errors.get("email")
        self.password_input.error_text = errors.get("password")
        self.confirm_password_input.error_text = errors.get("confirm_password")

        # Refresh the inputs to show errors
        self.first_name.update()
        self.last_name.update()
        self.email_input.update()
        self.password_input.update()
        self.confirm_password_input.update()

        # Check validation and terms agreement
        if is_valid and agree_terms:
            try:
                self.show_loading()
                self.page.run_task(self.send_otp_email)
            except Exception:
                pass

            # Save the values temporarily in client storage
            self.page.client_storage.set("register_first_name", first_name)
            self.page.client_storage.set("register_last_name", last_name)
            self.page.client_storage.set("register_email", email)
            self.page.client_storage.set("register_password", password)
            self.page.client_storage.set("register_confirm_pw", confirm_password)
            self.page.client_storage.set("register_terms", agree_terms)

    async def send_otp_email(self):
        first_name = self.first_name.value
        email = self.email_input.value

        response = await send_otp(email, first_name)

        if response.get("success"):
            print(response.get("message"))
            self.page.go("/otp")
        else:
            print(response.get("message"))

        self.hide_loading()
        

class OTPPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.email_address = self.page.client_storage.get("register_email") or None

    def build(self) -> ft.View:
        # Back button and header
        self.appbar = ft.AppBar(        
            leading=BackButton(
                on_click=lambda e: self.page.go("/register")
            ),
            title=ft.Container(
                content=ft.Text("Enter OTP", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # OTP input field
        self.otp_input = AppTextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            on_change= lambda e: self.otp_input.clear_error()
        )

        # Submit button
        self.submit_button = PrimaryButton(
            text="Submit",
            icon=ft.Icons.CHECK,
            on_click=self.on_submit,
        )

        # Resend OTP row
        self.resend_otp = ft.Row(
            controls=[
                ft.Text("Didn't receive the code?", size=14),
                CustomTextButton(
                    text="Resend OTP",
                    on_tap=self.on_resend
                )
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER
        )

        main_container = ft.Container(
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
                            ft.Text(self.email_address, size=14, color=ft.Colors.BLUE_ACCENT_100)
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
                    main_container
                ]
            )
        ]

        return self.layout(content, appbar=self.appbar)
    
    def on_submit(self, e):
        # If OTP input is empty
        if not self.otp_input.value:
            self.otp_input.error_text = "This field is required"
            self.otp_input.update()
            return

        # Otherwise, verify the OTP
        self.page.run_task(self.verify_otp_code)

    async def verify_otp_code(self):
        # Create the dialog first
        error_dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.ERROR),
            title=ft.Text("Invalid OTP"),
            content=ft.Text("The OTP you entered is incorrect. Please try again."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: clear_input(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def clear_input(e):
            self.otp_input.value = None
            self.page.close(error_dialog)
            self.otp_input.update()

        email = self.email_address
        entered_otp = self.otp_input.value

        self.show_loading()
        response = await verify_otp(email, entered_otp)

        if response.get("success"):
            print(response.get("message"))
            # self.page.client_storage.clear()
            # TODO: Remove client storage on valid otp (successful register)
            self.page.go("/home")
        else:
            print(response.get("message"))
            self.page.open(error_dialog)

        self.hide_loading()


    def on_resend(self, e):
        ...
