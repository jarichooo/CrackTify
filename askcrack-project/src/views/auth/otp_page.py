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
from services.otp_service import send_otp, verify_otp
from services.auth_service import register_user
from utils.input_validator import validate_registration

from config import Config

class OTPPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        # Loads the saved data
        self.saved_first_name = self.page.client_storage.get("register_first_name") or None
        self.saved_last_name = self.page.client_storage.get("register_last_name") or None
        self.saved_email = self.page.client_storage.get("register_email") or None
        self.saved_password = self.page.client_storage.get("register_password") or None

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
                            ft.Text(self.saved_email, size=14, color=ft.Colors.BLUE_ACCENT_100)
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
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
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
        """Verify the entered OTP code"""
        entered_otp = self.otp_input.value

        def clear_input(e):
            # Clear the OTP input field
            self.otp_input.value = None
            self.page.close(invalid_otp_dialog)
            self.otp_input.update()

        # Create the dialog first
        invalid_otp_dialog = ErrorDialog(
            title=ft.Text("Invalid OTP"),
            content=ft.Text("The OTP you entered is incorrect. Please try again."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: clear_input(e))
            ]
        )

        response = await verify_otp(self.saved_email, entered_otp)

        if response.get("success"):
            print(response.get("message"))
        
            reg_response = await register_user(
                self.saved_first_name,
                self.saved_last_name,
                self.saved_email,
                self.saved_password,
            )

            if reg_response.get("success"):
                print(reg_response.get("message"))
                token = reg_response.get("token")
                user = reg_response.get("user")

                # Save token to client storage
                await self.page.client_storage.set_async("auth_token", token)
                await self.page.client_storage.set_async("user_info", user)

                self.page.run_task(self.clear_values)
                self.page.go("/home")
            else:
                self.page.open(ErrorDialog(
                    title=ft.Text("Registration Failed"),
                    content=ft.Text("An error occurred during registration. Please try again."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: self.page.close())
                    ]
                ))

        else:
            print(response.get("message"))
            self.page.open(invalid_otp_dialog)

        self.hide_loading()

    async def clear_values(self):
        try:
            await self.page.client_storage.remove_async("register_first_name")
            await self.page.client_storage.remove_async("register_last_name")
            await self.page.client_storage.remove_async("register_email")
            await self.page.client_storage.remove_async("register_password")
            await self.page.client_storage.remove_async("register_confirm_pw")
            await self.page.client_storage.remove_async("register_terms")

        except Exception as e:
            print(f"Error clearing client storage: {e}")

    def on_resend(self, e):
        ...
