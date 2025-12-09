import flet as ft

from views.template import TemplatePage
from widgets.buttons import (
    BackButton,
    PrimaryButton,
    GoogleButton,
    CustomTextButton
)
from widgets.divider import or_divider
from widgets.inputs import AppTextField
from widgets.dialogs import ErrorDialog
from services.otp_service import send_otp
from services.auth_service import check_email_unique
from utils.input_validator import validate_registration

from config import Config

class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        
    def build(self) -> ft.View:
        """Build the registration page UI"""
        # Loads saved values
        self.saved_first_name = self.page.client_storage.get("register_first_name") or None
        self.saved_last_name = self.page.client_storage.get("register_last_name") or None
        self.saved_email = self.page.client_storage.get("register_email") or None
        self.saved_password = self.page.client_storage.get("register_password") or None
        self.saved_confirm_pw = self.page.client_storage.get("register_confirm_pw") or None
        self.saved_terms = self.page.client_storage.get("register_terms") or None

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

        # Google Register Button
        self.google_register = GoogleButton(
            text="Sign up with Google",
            on_click=self.google_register_clicked,
        )

        # Inputs
        self.first_name = AppTextField(
            value=self.saved_first_name,
            label="First Name",
            hint_text="Enter your first name",
            expand=1,
            on_change=lambda e: self.first_name.clear_error()
        )

        self.last_name = AppTextField(
            value=self.saved_last_name,
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

        # Main content container
        main_container = ft.Container(
            width=500,
            content= ft.ListView(
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
                        spacing=8,
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
            padding=ft.padding.only(top=30, bottom=0),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(top_left=30, top_right=30),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            expand=True
        )

        # Page layout
        content = [
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(),
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

        # Initalize error dialog for not checking checkbox
        error_dialog = ErrorDialog(
            title=ft.Text("Agreement Required"),
            content=ft.Text("You must accept the Terms and Conditions before proceeding"),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
            ]
        )

        # Validate input values
        is_valid, errors = validate_registration(first_name, last_name, email, password, confirm_password)
        
        # Check validation and terms agreement
        if is_valid and agree_terms:
    
            try:
                self.show_loading()
                # Save the values temporarily in client storage
                self.page.client_storage.set("register_first_name", first_name)
                self.page.client_storage.set("register_last_name", last_name)
                self.page.client_storage.set("register_email", email)
                self.page.client_storage.set("register_password", password)
                self.page.client_storage.set("register_confirm_pw", confirm_password)
                self.page.client_storage.set("register_terms", agree_terms)

                self.page.run_task(self.check_email) # First check if email is unique

            except Exception as ex:
                print("Error during registration process:", ex)

        elif not is_valid:
            # Display errors
            self.first_name.error_text = errors.get("first_name", "")       
            self.last_name.error_text = errors.get("last_name", "")
            self.email_input.error_text = errors.get("email", "")
            self.password_input.error_text = errors.get("password", "")
            self.confirm_password_input.error_text = errors.get("confirm_password", "")

            self.first_name.update()
            self.last_name.update()
            self.email_input.update()
            self.password_input.update()
            self.confirm_password_input.update()

        elif not agree_terms:
            self.page.open(error_dialog) # Show error dialog if terms not agreed


    async def check_email(self):
        email = self.email_input.value

        error_dialog = ErrorDialog(
            title=ft.Text("Email Already Registered"),
            content=ft.Text("The email you entered is already registered. Please use a different email."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
            ]
        )
        response = await check_email_unique(email)

        if not response.get("success"):
            # If email is not unique, show error dialog
            self.hide_loading()
            self.page.open(error_dialog)
        else:
            # If email is unique, proceed to send OTP
            self.page.run_task(self.send_otp_email) # Send OTP email
    
    async def send_otp_email(self):
        first_name = self.first_name.value
        email = self.email_input.value

        response = await send_otp(email, first_name)
        self.hide_loading()

        if response.get("success"):
            print(response.get("message"))
            self.page.go("/otp")
        else:
            print(response.get("message"))

    def google_register_clicked(self, e):
        ...