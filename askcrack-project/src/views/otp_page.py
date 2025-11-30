import flet as ft

from .template import TemplatePage
from widgets.buttons import (
    BackButton,
    PrimaryButton,
    GoogleButton,
    CustomTextButton
)
from widgets.divider import or_divider
from widgets.inputs import AppTextField
from widgets.dialogs import ErrorDialog
from services.otp_service import send_otp, verify_otp
from utils.input_validator import validate_registration

from config import Config

class OTPPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        # Loads the saved email address
        self.email_address = self.page.client_storage.get("register_email") or None

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
        self.show_loading()
        self.page.run_task(self.verify_otp_code)

    async def verify_otp_code(self):
        # Create the dialog first
        email = self.email_address
        entered_otp = self.otp_input.value

        invalid_otp_dialog = ErrorDialog(
            title=ft.Text("Invalid OTP"),
            content=ft.Text("The OTP you entered is incorrect. Please try again."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: clear_input(e))
            ]
        )

        def clear_input(e):
            self.otp_input.value = None
            self.page.close(invalid_otp_dialog)
            self.otp_input.update()

        response = await verify_otp(email, entered_otp)

        if response.get("success"):
            print(response.get("message"))
            # TODO: Add register user logic
            self.page.run_task(self.clear_values)
            self.page.go("/home")

        else:
            print(response.get("message"))
            self.page.open(invalid_otp_dialog)

        self.hide_loading()

    async def clear_values(self):
        try:
            await self.page.client_storage.clear()
        except:
            pass

    def on_resend(self, e):
        ...
