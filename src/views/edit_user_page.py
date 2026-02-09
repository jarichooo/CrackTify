import json
import flet as ft

from .template import TemplatePage

from widgets.buttons import PrimaryButton, SecondaryButton
from widgets.inputs import TextField
from widgets.dialogs import AlertDialog

from services.profile_service import update_profile
from services.otp_service import send_otp, verify_otp
from services.file_service import upload_file


class EditUserPage(TemplatePage):
    def __init__(self, page: ft.Page, user, on_save=None):
        super().__init__(page)
        
        # Store user data for editing
        self.user = user
        self.on_save = on_save

        self.user_id = user.get("id")
        self.user_avatar_url = user.get("avatar_url")
        self.user_first_name = user.get("first_name")
        self.user_last_name = user.get("last_name")
        self.user_email = user.get("email_address")

        self.verified_email = self.user_email # Track the currently verified email address

    def build(self) -> ft.View:
        # AppBar with back button and title
        app_bar = ft.AppBar(
            title=ft.Text("Edit Account Information"),
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.views.pop()),
            force_material_transparency=True
        )

        # Avatar with edit overlay
        self.avatar_image = ft.Container(
            height=200,
            width=200,
            border_radius=100,
            bgcolor=ft.Colors.GREY_300,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(
                src=self.user_avatar_url,
                fit=ft.BoxFit.COVER,
            )
        )

        # Stack the avatar image with a camera icon overlay for editing
        self.avatar_control = ft.Container(
            ft.Stack(
                controls=[
                    self.avatar_image,
                    ft.Container(
                        content=ft.Icon(ft.Icons.CAMERA_ALT, size=20, color=ft.Colors.WHITE),
                        width=30,
                        height=30,
                        bgcolor=ft.Colors.BLACK_54,
                        border_radius=20,
                        alignment=ft.Alignment.CENTER,
                        on_click=self.on_avatar_click
                    )
                ],
                alignment=ft.Alignment.BOTTOM_RIGHT
            ),
            alignment=ft.Alignment.CENTER
        )

        # Editable Fields
        self.first_name_field = TextField(
            label="First Name",
            border=ft.InputBorder.NONE,
            value=self.user_first_name,
        )

        self.last_name_field = TextField(
            label="Last Name",
            border=ft.InputBorder.NONE,
            value=self.user_last_name,
        )

        self.email_field = TextField(
            label="Email",
            border=ft.InputBorder.NONE,
            value=self.user_email,
            suffix_icon=ft.Button(
                content="Verify email",
                visible=False,
                on_click=self.on_verify_click
            ),
            on_change=self.allow_change_email # Show verify button if email is changed
        )

        # Save Changes Button
        self.save_button = PrimaryButton(
            text="Save Changes",
            icon=ft.Icons.SAVE,
            width=300,
            height=45,
            expand=True,
            on_click=self.save_changes
        )


        # Layout the page content
        self.body = ft.Container(
            padding=ft.Padding.all(20),
            content=ft.ListView(
                spacing=20,
                controls=[
                    self.avatar_control,
                    self.first_name_field,
                    self.last_name_field,
                    self.email_field,
                    self.save_button,
                ]
            )
        )

        return self.layout(
            route="/edit",
            appbar=app_bar,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.body
            ]
        )
    
    def allow_change_email(self):
        """Show the verify email button if the email field value is changed from the original email."""
        if self.email_field.value.strip() != self.user_email:
            self.email_field.suffix_icon.visible = True
        else:
            self.email_field.suffix_icon.visible = False

    async def on_verify_click(self):
        """Handle verify email button click to send OTP and show verification dialog."""
        new_email = self.email_field.value.strip()
        
        self.show_loading()
        otp_response = await send_otp(new_email, self.user_first_name)

        self.otp_field = TextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
        )

        self.otp_dialog = AlertDialog(
            title="Verify Email",
            modal=True,
            content=ft.Container(
                ft.Column(
                    height=150,
                    controls=[
                        ft.Text("A 6-digit verification code has been sent to", size=14),
                        ft.Text(new_email, size=14, color=ft.Colors.BLUE_ACCENT_100),
                        self.otp_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: self.page.pop_dialog()
                ),
                ft.TextButton(
                    "Verify",
                    on_click=lambda _:  self.page.run_task(self.verify_new_email, self.otp_field.value, new_email)
                )
            ]
        )

        self.hide_loading()
        if otp_response.get("success"):
            self.page.show_dialog(self.otp_dialog)
        else:
            self.page.show_dialog(
                AlertDialog(
                    title="Error Verifying Email",
                    content=otp_response.get("message")
                )
            )

    async def verify_new_email(self, otp_value, email):
        """Verify the OTP entered by the user and update the verified email if successful."""
        self.otp_field.suffix_icon = ft.Container(
            ft.ProgressRing(height=20, width=20)
        )
        self.page.update()

        response = await verify_otp(email, otp_value)

        if not response.get("success"):
            self.otp_field.suffix_icon = None
            self.otp_field.error = "Your OTP is incorrect. Try again."
            self.page.update()
            return
        
        self.verified_email = email
        
        self.page.pop_dialog()
        self.page.show_dialog(
            ft.SnackBar(f"{email} has been verified.", bgcolor=ft.Colors.GREEN_500)
        )
            
    async def on_avatar_click(self, e):
        """Handle avatar image click to pick a new image file."""
        self.file_picker = ft.FilePicker()

        files = await self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])
        if not files:
            return
        
        file = files[0]
        self.picked_file = file

        # Update avatar image
        self.avatar_image.content.src = file.path

    async def save_changes(self):
        updates = {}

        # Current values (from stored user)
        current_first = self.user.get("first_name", "")
        current_last = self.user.get("last_name", "")
        current_avatar = self.user.get("avatar_url", "")
        current_email = self.user.get("email_address", "")

        # New values (from UI)
        new_first = self.first_name_field.value.strip()
        new_last = self.last_name_field.value.strip()
        new_avatar = self.avatar_image.content.src

        # Compare text fields
        if new_first and new_first != current_first:
            updates["first_name"] = new_first

        if new_last and new_last != current_last:
            updates["last_name"] = new_last

        if self.verified_email != current_email:
            updates["email_address"] = self.verified_email

        # Compare avatar (upload only if changed)
        if new_avatar and new_avatar != current_avatar:
            try:
                upload_response = await upload_file(new_avatar)
                updates["avatar_url"] = upload_response.get("url", current_avatar)
            except Exception:
                pass  # Keep old avatar if upload fails

        # If nothing changed, skip API call
        if not updates:
            self.page.views.pop()
            return

        # Required identifier
        updates["id"] = self.user_id

        self.show_loading()
        response = await update_profile(updates)
        self.hide_loading()

        if not response.get("success"):
            self.page.show_dialog(
                AlertDialog(
                    title="Saving error",
                    content="Error saving changes, please try again."
                )
            )
            return

        # Update local user cache
        updated_user = {**self.user, **response.get("user", {})}
        await self.page.shared_preferences.set("user", json.dumps(updated_user))

        if hasattr(self, "on_save"):
            self.on_save(updated_user)
            print("Updated user data passed to on_save callback:", updated_user) # Debug print to check updated user data

        self.page.views.pop()
