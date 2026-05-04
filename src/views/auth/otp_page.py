import asyncio
import json
import time
import flet as ft

from services.auth_service import register_user
from views.verify_engineer import VerifyEngineerPage
from views.template import TemplatePage
from services.otp_service import verify_otp, send_otp
from widgets.inputs import TextField
from widgets.dialogs import AlertDialog
from widgets.buttons import BackButton, PrimaryButton, CustomTextButton

from model.user import User


class OTPVerificationPage(TemplatePage):
    def __init__(
        self,
        page: ft.Page,
        email_address: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
        is_engineer: bool = False,
    ):
        super().__init__(page)
        self.email_address = email_address
        self.username = username
        self.first_name = first_name
        self.is_engineer = is_engineer
        self.last_name = last_name
        self.password = password

        self._is_processing = False  # guard flag

    def build(self) -> ft.View:
        self.otp_field = TextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
        )

        self.resend_button = CustomTextButton(
            text="Resend OTP",
            color=ft.Colors.BLUE,
            on_tap=lambda e: asyncio.create_task(self.handle_resend_otp(e)),
        )

        self.submit_button = PrimaryButton(
            text="Verify OTP",
            icon=ft.Icons.CHECK,
            disabled=self._is_processing,
            on_click=lambda e: asyncio.create_task(self.handle_verify_otp(e)),
        )

        main_container = ft.Container(
            width=500,
            content=ft.ListView(
                expand=True,
                padding=20,
                spacing=15,
                controls=[
                    ft.Column(
                        [
                            ft.Text("Verify your email", size=28, weight="bold"),
                            ft.Text(
                                "A 6-digit authentication code has been sent to",
                                size=14,
                            ),
                            ft.Text(
                                self.email_address,
                                size=14,
                                color=ft.Colors.BLUE_ACCENT_100,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.horizontal_divider(opacity=0),
                    self.otp_field,
                    self.submit_button,
                    ft.Row(
                        [ft.Text("Didn't receive the OTP?"), self.resend_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    ),
                ],
            ),
            padding=ft.Padding.only(top=50),
            alignment=ft.Alignment.CENTER,
            border_radius=30,
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            expand=True,
        )

        return self.layout(
            route="/otp-verification",
            appbar=ft.AppBar(
                title=ft.Text("OTP Verification"),
                center_title=True,
                force_material_transparency=True,
                leading=BackButton(on_click=lambda e: self.page.views.pop()),
            ),
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[ft.Container(), main_container],
                )
            ],
        )

    async def handle_verify_otp(self, e):
        entered_otp = self.otp_field.value
        if not entered_otp or len(entered_otp) != 6:
            self.page.show_dialog(
                AlertDialog(
                    title="Invalid OTP", content="Please enter the 6-digit OTP."
                )
            )
            return

        self.submit_button.disabled = True
        self.resend_button.disabled = True
        self.page.update()
        self.show_loading()

        try:
            response = await verify_otp(self.email_address, entered_otp)

            if not response.get("success"):
                self.page.show_dialog(
                    AlertDialog(
                        title="Invalid OTP",
                        content="The OTP you entered is incorrect. Please try again.",
                    )
                )
                return

            reg_response = await register_user(
                self.first_name,
                self.last_name,
                self.username,
                self.email_address,
                self.password,
                self.is_engineer,
            )

            # Check registration response
            if not reg_response.get("success"):
                self.page.show_dialog(
                    AlertDialog(
                        title="Registration Failed",
                        content=reg_response.get("message", "Registration failed."),
                    )
                )
                return

            user_data = reg_response.get("user", {}) # Extract user data from registration response

            await self.page.shared_preferences.set(
                "auth_token", reg_response.get("token")
            )
            await self.page.shared_preferences.set(
                "user", json.dumps(user_data)
            )

            User.from_dict(user_data)  # Update User model with new data

            # if self.is_engineer:
            #     """If user is an engineer, upload extra verification documents and """
            #     from views.auth.verify_engineer import VerifyEngineerPage
                
            #     await self.page.push_view(VerifyEngineerPage(self.page))
            #     return
            
            await self.page.push_route("/home") # Navigate to home after successful registration

        finally:
            self.hide_loading()
            self.submit_button.disabled = False
            self.resend_button.disabled = False
            self.page.update()

    async def handle_resend_otp(self, e):
        if self._is_processing:
            return

        self._is_processing = True
        self.page.update()
        self.show_loading()

        response = await send_otp(self.email_address, self.first_name, resend=True)

        if response.get("success"):

            self.page.show_dialog(
                AlertDialog(
                    title="OTP Sent",
                    content="A new OTP has been sent to your email address.",
                )
            )
            asyncio.create_task(self.countdown(300))
        else:
            self._is_processing = False
            self.page.show_dialog(
                AlertDialog(
                    title="Error",
                    content=response.get("message", "Failed to resend OTP."),
                )
            )
            
        self.hide_loading()
        self.page.update()

    async def countdown(self, seconds):
        """ Disables the resend button and shows a countdown until it can be used again. """
        self.resend_button.disabled = True
        self.resend_button.content.color = ft.Colors.GREY
        self.resend_button.update()

        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            self.resend_button.content.value = f"Wait {mins:02d}:{secs:02d}"
            self.resend_button.update()
            await asyncio.sleep(1)
            seconds -= 1

        # Reset button
        self.resend_button.content.value = "Resend OTP"
        self.resend_button.content.color = ft.Colors.BLUE
        self.resend_button.disabled = False
        self._is_processing = False
        self.resend_button.update()