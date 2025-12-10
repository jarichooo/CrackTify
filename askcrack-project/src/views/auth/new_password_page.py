import flet as ft

from views.template import TemplatePage
from widgets.buttons import (
    BackButton,
    PrimaryButton
)
from widgets.inputs import AppTextField
from utils.input_validator import validate_password_change
from services.auth_service import forgot_password

class ForgotPasswordPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Build the forgot password page UI"""
        # Back button and header
        self.appbar = ft.AppBar(
            leading=BackButton(
                on_click=lambda e: self.page.go("/login")
            ),
            title=ft.Container(
                content=ft.Text("New Password", size=18, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            center_title=True,
            force_material_transparency=True
        )

        # New Password Input
        self.new_password_input = AppTextField(
            label="New Password",
            hint_text="Enter your new password",
            autofocus=True,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.new_password_input.clear_error()
        )

        # Confirm Password Input
        self.confirm_password_input = AppTextField(
            label="Confirm Password",
            hint_text="Re-enter your new password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self.confirm_password_input.clear_error()
        )

        # Submit Button
        self.submit_button = PrimaryButton(
            text="Reset Password",
            icon=ft.Icons.CHECK,
            on_click=lambda e: self.page.run_task(self.on_submit),
        )

        main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.new_password_input,
                    self.confirm_password_input,
                    ft.Divider(opacity=0),
                    self.submit_button,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=20,
            ),  
            padding=ft.padding.symmetric(horizontal=20, vertical=30)
        )

        return self.layout([main_container], appbar=self.appbar)

    async def on_submit(self):
        """Handle submit button click"""
        new_password = self.new_password_input.value
        confirm_password = self.confirm_password_input.value

        is_valid, errors = validate_password_change(
            current_password=None,
            new_password=new_password,
            confirm_password=confirm_password
        )

        # Display validation errors if any
        if not is_valid:
            if "new_password" in errors:
                self.new_password_input.error_text = errors["new_password"]
            if "confirm_password" in errors:
                self.confirm_password_input.error_text = errors["confirm_password"]

            self.page.update()
            return

        # Get email from client storage
        email = await self.page.client_storage.get_async("reset_email")


        # Call forgot password service
        self.show_loading()
        response = await forgot_password(email, new_password)

        if response.get("success"):
            self.hide_loading()
            success_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Success"),
                content=ft.Text("Your password has been reset successfully. Please log in with your new password."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.go("/login"))
                ]
            )
            await self.page.client_storage.remove_async("reset_email")
            self.page.open(success_dialog)
        else:
            self.hide_loading()
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Error"),
                content=ft.Text(response.get("message", "Failed to reset password. Please try again.")),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.close(error_dialog))
                ]
            )
            self.page.open(error_dialog)

        self.page.update()