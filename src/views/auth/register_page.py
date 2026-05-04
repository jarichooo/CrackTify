import asyncio
import json
from urllib import response

import flet as ft

from services.auth_service import check_uniqueness
from services.otp_service import send_otp
from utils.input_validation import validate_registration

from views.template import TemplatePage
from views.auth.otp_page import OTPVerificationPage

from widgets.inputs import TextField
from widgets.buttons import (
    PrimaryButton,
    SecondaryButton,
    GoogleButton,
    CustomTextButton,
    BackButton,
)
from widgets.dialogs import AlertDialog


class RegisterPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Builds the registration Page layout."""
        self.first_name_field = TextField(
            label="First Name",
            hint_text="Enter your first name",
            autofocus=True,
            expand=1,
            value=self.saved_user.get("first_name", ""),
        )

        self.last_name_field = TextField(
            label="Last Name",
            hint_text="Enter your last name",
            expand=1,
            value=self.saved_user.get("last_name", ""),
        )

        self.username_field = TextField(
            label="Username",
            hint_text="Choose a username",
            value=self.saved_user.get("username", ""),
        )

        self.email_field = TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
            value=self.saved_user.get("email_address", ""),
        )

        self.password_field = TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            value=self.saved_user.get("password_1", ""),
        )

        self.confirm_password_field = TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            value=self.saved_user.get("password_2", ""),
        )

        self.role_group = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(label="Civilian", value="civilian"),
                    ft.Radio(label="Structural Engineer", value="engineer"),
                ]
            ),
            value=self.saved_user.get("is_engineer", False) and "engineer" or "civilian", # Set default value based on saved_user else default to "civilian"
        )

        continue_button = PrimaryButton(
            text="Continue",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=lambda _: self.page.run_task(self.on_continue_click),
        )

        header_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(
                        src="splash_android.png",
                        width=100,
                        height=100,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    ft.Text("Cracktify", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Detect cracks, prevent risks, ensure safety.",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.padding.only(top=-50, bottom=30),
        )

        main_container = self.main_container(
            content=ft.ListView(
                padding=ft.Padding.only(left=20, right=20),
                spacing=15,
                auto_scroll=False,
                controls=[
                    ft.Text(
                        "Create Your Account",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    self.horizontal_divider(height=1, opacity=0),
                    ft.Row(
                        spacing=10,
                        controls=[self.first_name_field, self.last_name_field],
                    ),
                    self.username_field,
                    self.email_field,
                    self.password_field,
                    self.confirm_password_field,
                    ft.Text(
                        "Select Your Role",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            self.role_group,
                        ],
                    ),
                    self.horizontal_divider(height=1, opacity=0),
                    continue_button,
                    self.horizontal_divider(height=20, opacity=0),
                ],
            ),
        )

        return self.layout(
            route="/register",
            appbar=ft.AppBar(
                leading=BackButton(
                    on_click=lambda _: self.page.views.pop(),
                ),
                force_material_transparency=True
            ),
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        header_section,
                        main_container,
                    ],
                ),
            ]
        
        )

    async def on_continue_click(self):
        """Handle continue button click"""
        first_name = self.first_name_field.value.strip()
        last_name = self.last_name_field.value.strip()
        username = self.username_field.value.strip()
        email = self.email_field.value.strip()
        password = self.password_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()

        # Validate input values
        is_valid, errors = validate_registration(
            first_name, last_name, username, email, password, confirm_password
        )

        if not is_valid:
            # Display validation errors
            self.first_name_field.error = errors.get("first_name")
            self.last_name_field.error = errors.get("last_name")
            self.username_field.error = errors.get("username")
            self.email_field.error = errors.get("email")
            self.password_field.error = errors.get("password")
            self.confirm_password_field.error = errors.get("confirm_password")
            self.page.update()
            return

        # Inputs are valid → proceed
        self.show_loading()

        try:
            # Save user input temporarily in shared preferences
            saved_user = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email_address": email,
                "password_1": password,
                "password_2": confirm_password,
                "is_engineer": self.role_group.value == "engineer",
            }
            await self.page.shared_preferences.set("saved_user", json.dumps(saved_user))

            # Verify email and username uniqueness and send OTP in parallel to reduce wait time
            await self.handle_send_otp(email, username, first_name)

        except Exception as ex:
            self.hide_loading()
            self.page.show_dialog(
                AlertDialog(
                    title="Error",
                    content=f"Unexpected error: {ex}",
                )
            )

    async def handle_send_otp(self, email, username, first_name):
        # Check if email is unique
        email_response = await check_uniqueness(email, "email")
        if not email_response.get("success"):
            self.hide_loading()
            self.page.show_dialog(
                AlertDialog(
                    title="Email Already Exists",
                    content="The email address is already registered.",
                )
            )
            return
        
        # Check if username is unique
        username_response = await check_uniqueness(username, "username")
        if not username_response.get("success"):
            self.hide_loading()
            self.page.show_dialog(
                AlertDialog(
                    title="Username Already Exists",
                    content="The username is already taken.",
                )
            )
            return

        # Send OTP and **await** response
        otp_response = await send_otp(email, first_name)
        self.hide_loading()  # hide loading after response

        if not otp_response.get("success"):
            self.page.show_dialog(
                AlertDialog(
                    title="OTP Failed",
                    content=otp_response.get("message", "Failed to send OTP"),
                )
            )
            return


        # Navigate to OTP page only if OTP succeeded
        self.page.views.append(
            OTPVerificationPage(
                self.page,
                email,
                username,
                first_name,
                self.last_name_field.value,
                self.password_field.value,
                is_engineer=self.role_group.value == "engineer",
            ).build()
        )
        self.page.update()
