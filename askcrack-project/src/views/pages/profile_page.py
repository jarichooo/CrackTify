import flet as ft
import os
import shutil
from datetime import datetime
from pathlib import Path

from widgets.inputs import AppTextField
from widgets.buttons import PrimaryButton, SecondaryButton, CustomTextButton
from services.profile_service import verify_user_password, update_profile, delete_account
from services.otp_service import send_otp, verify_otp
from utils.image_utils import image_to_base64, base64_to_image
from utils.input_validator import validate_password_change

class ProfilePage:
    def __init__(self, page: ft.Page):
        self.page = page

        # --- THEME MODE RESTORE ---
        saved_theme_mode = self.page.client_storage.get("theme_mode")
        if saved_theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif saved_theme_mode == "system":
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        # --- THEME COLOR RESTORE ---
        saved_theme_color = self.page.client_storage.get("theme_color")
        if saved_theme_color:
            color_map = {
                "red": ft.Colors.RED,
                "blue": ft.Colors.BLUE,
                "green": ft.Colors.GREEN,
                "yellow": ft.Colors.YELLOW,
            }
            chosen = color_map.get(saved_theme_color.lower(), ft.Colors.BLUE)
            self.page.theme = ft.Theme(color_scheme_seed=chosen)

            self.new_email = None  # To store new email during change process
        # ----------------------------

    def build(self) -> ft.Control:
        """Build the profile page UI"""
        self.user = self.page.client_storage.get("user_info")  # Load user data from client storage
        self.user_first_name = self.user.get("first_name", "")
        self.user_last_name = self.user.get("last_name", "")
        self.user_email = self.user.get("email", "")
        self.user_avatar_base64 = self.user.get("avatar_base64", "")

        self.full_name = f"{self.user_first_name} {self.user_last_name}".strip()

        # FilePicker for avatar
        avatar_picker = ft.FilePicker(on_result=self.on_avatar_picked)
        self.page.overlay.append(avatar_picker)

        # Rounded image (instead of CircleAvatar)
        self.avatar_image = ft.Container(
            width=100,
            height=100,
            border_radius=50,  # half of width/height for perfect circle-like round image
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(
                src_base64=self.user_avatar_base64,
                fit=ft.ImageFit.COVER,
            )
        )

        # Camera button overlay stays the same
        self.avatar_control = ft.Stack(
            controls=[
                self.avatar_image,
                ft.Container(
                    content=ft.Icon(ft.Icons.CAMERA_ALT, size=20, color="white"),
                    width=30,
                    height=30,
                    bgcolor=ft.Colors.BLACK54,
                    border_radius=20,
                    alignment=ft.alignment.center,
                    on_click=lambda e: avatar_picker.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["png", "jpg", "jpeg"]
                    )
                )
            ],
            alignment=ft.alignment.bottom_right
        )


        # Editable Fields
        self.first_name_input = AppTextField(
            label="First Name",
            border=ft.InputBorder.UNDERLINE,
            value=self.user_first_name,
            expand=1
        )
        self.last_name_input = AppTextField(
            label="Last Name",
            border=ft.InputBorder.UNDERLINE,
            value=self.user_last_name,
            expand=1
        )

        self.full_name_text = ft.Text(self.full_name, size=20, weight="bold")

        self.email_input = AppTextField(
            label="Email",
            border=ft.InputBorder.NONE,
            value=self.user_email,
            suffix_icon=ft.IconButton(icon=ft.Icons.EDIT, on_click=self.allow_email_change),
            read_only=True,
        )

        self.otp_input = AppTextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            on_change= lambda e: self.otp_input.clear_error()
        )
        
        save_button = PrimaryButton(
            text="Save Changes",
            icon=ft.Icons.SAVE,
            width=300,
            height=45,
            expand=True,
            on_click=self.save_profile_changes
        )

        logout_button = SecondaryButton(
            text="Logout",
            icon=ft.Icons.LOGOUT,
            width=300,
            height=45,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.RED_100,
                    ft.ControlState.HOVERED: ft.Colors.RED_200,
                    ft.ControlState.PRESSED: ft.Colors.RED_300,
                },
                color=ft.Colors.RED_700,
                icon_color=ft.Colors.RED_700,
            ),
            on_click=lambda e: self.page.go("/logout"),
        )

        button_column = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[save_button, logout_button],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        # --- THEME MODE HANDLER ---
        def handle_theme_mode(e):
            selected = e.control.text.lower()
            if selected == "light":
                mode = ft.ThemeMode.LIGHT
                mode_str = "light"
            elif selected == "dark":
                mode = ft.ThemeMode.DARK
                mode_str = "dark"
            else:
                mode = ft.ThemeMode.SYSTEM
                mode_str = "system"

            self.page.theme_mode = mode
            self.page.client_storage.set("theme_mode", mode_str)
            self.page.update()

        # --- THEME COLOR HANDLER ---
        def handle_theme_color(e):
            color_name = e.control.text.lower()
            color_map = {
                "red": ft.Colors.RED,
                "blue": ft.Colors.BLUE,
                "green": ft.Colors.GREEN,
                "yellow": ft.Colors.YELLOW,
            }
            chosen = color_map.get(color_name, ft.Colors.BLUE)
            self.page.theme = ft.Theme(color_scheme_seed=chosen)
            self.page.client_storage.set("theme_color", color_name)
            self.page.update()

        panel_list = ft.ExpansionPanelList(
            elevation=0,
            divider_color=ft.Colors.TRANSPARENT,
            controls=[
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Account Information", weight="bold", size=16),
                        alignment=ft.alignment.center_left,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[self.first_name_input, self.last_name_input],
                                spacing=20,
                            ),
                            self.email_input,
                        ],
                        tight=True,
                    ),
                ),
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Security", weight="bold", size=16),
                        alignment=ft.alignment.center_left,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Change Password"),
                                on_click=self.open_change_password_dialog
                            ),
                        ],
                        tight=True,
                    ),
                ),
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Preferences", weight="bold", size=16),
                        alignment=ft.alignment.center_left,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Theme Mode"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(text="Light", on_click=handle_theme_mode),
                                        ft.PopupMenuItem(text="Dark", on_click=handle_theme_mode),
                                        ft.PopupMenuItem(text="System", on_click=handle_theme_mode),
                                    ],
                                )
                            ),
                            ft.ListTile(
                                title=ft.Text("Theme Color"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(text="Red", on_click=handle_theme_color),
                                        ft.PopupMenuItem(text="Blue", on_click=handle_theme_color),
                                        ft.PopupMenuItem(text="Green", on_click=handle_theme_color),
                                        ft.PopupMenuItem(text="Yellow", on_click=handle_theme_color),
                                    ],
                                )
                            ),
                        ],
                        tight=True,
                    ),
                ),
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Data and Privacy", weight="bold", size=16),
                        alignment=ft.alignment.center_left,
                    ),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.START,
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Download My Data"),
                                on_click=lambda e: self.page.run_task(self.download_pdf),
                            ),
                            ft.ListTile(
                                title=ft.Text("Delete My Account", color=ft.Colors.RED_100),
                                on_click=self.delete_account,
                            ),
                        ],
                        tight=True,
                    ),
                ),

            ]
        )

        self.list_view = ft.ListView(
            expand=True,
            controls=[
                panel_list,
                button_column,
            ],
            spacing=10,
        )

        # Update body
        return [
            self.avatar_control,
            self.full_name_text,
            ft.Divider(height=15, opacity=0),
            self.list_view,
        ]
    
    def allow_email_change(self, e):
        """Enable email input for editing and send OTP"""
        self.email_input.read_only = False
        self.email_input.border = ft.InputBorder.UNDERLINE
        self.email_input.focus()
        
        # Create new OTP input for each attempt
        self.otp_input = AppTextField(
            label="One-Time PIN",
            hint_text="XXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
            on_change=lambda e: self.otp_input.clear_error()
        )

        self.email_input.suffix_icon = ft.IconButton(
            icon=ft.Icons.CHECK,
            on_click=self.send_otp_for_email_change
        )
        self.page.update()

    def send_otp_for_email_change(self, e):
        """Send OTP to the new email before showing verification dialog"""
        self.new_email = self.email_input.value.strip()

        if self.new_email == self.user_email.strip():
            self.email_input.suffix_icon = ft.IconButton(icon=ft.Icons.EDIT, on_click=self.allow_email_change)
            self.email_input.read_only = True
            self.email_input.border = ft.InputBorder.NONE
            self.page.update()
            return
        
        if not self.new_email:
            self.email_input.error_text = "Email cannot be empty"
            self.page.update()
            return

        # Send OTP asynchronously
        self.page.run_task(self._send_otp_task)

    async def _send_otp_task(self):
        self.email_input.suffix_icon = ft.Container(ft.ProgressRing(width=8, height=8))
        self.email_input.update()
        first_name = self.first_name_input.value
        response = await send_otp(self.new_email, first_name)
        if response.get("success"):
            # Show OTP dialog after OTP sent
            self.show_otp_dialog()
        else:
            self.email_input.error_text = "Failed to send OTP. Try again."
            self.page.update()

    def show_otp_dialog(self):
        """Open OTP verification dialog"""
        self.verify_email_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Email Change"),
            inset_padding=ft.padding.all(20),
            content=ft.Container(
                ft.Column(
                    height=150, 
                    controls=[
                        ft.Text("A 6-digit verification code has been sent to your new email. Enter it below:"),
                        self.otp_input
                    ],
                )
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.update_suffix_icon_on_cancel()),
                ft.TextButton("Verify", on_click=lambda e: self.page.run_task(self.verify_email_change))
            ]
        )
        self.page.open(self.verify_email_dialog)

    def update_suffix_icon_on_cancel(self):
        """Reset email input suffix icon on OTP dialog cancel"""
        self.email_input.suffix_icon = ft.IconButton(icon=ft.Icons.CHECK, on_click=self.allow_email_change)
        self.page.close(self.verify_email_dialog)
        self.page.update()

    async def verify_email_change(self):
        """Verify OTP and update email if correct"""
        entered_otp = self.otp_input.value.strip()
        self.new_email = self.email_input.value.strip()
        
        if not entered_otp:
            self.otp_input.error_text = "OTP cannot be empty"
            self.page.update()
            return

        response = await verify_otp(self.new_email, entered_otp)
        if response.get("success"):
            # OTP verified, update email
            self.user["email"] = self.new_email
            self.email_input.read_only = True
            self.email_input.border = ft.InputBorder.NONE
            self.email_input.suffix_icon = ft.IconButton(icon=ft.Icons.EDIT, on_click=self.allow_email_change)
            self.page.close(self.verify_email_dialog)
            self.page.update()
            print("Email updated successfully.")
        else:
            self.otp_input.error_text = "Invalid OTP. Please try again."
            self.page.update()

    def on_avatar_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        avatar_path = e.files[0].path
        print(avatar_path)
        avatar_base64 = image_to_base64(avatar_path)
        self.user["avatar_base64"] = avatar_base64
        self.avatar_image.content.src_base64 = avatar_base64
        self.avatar_image.content.update()

    def open_change_password_dialog(self, e):
        """Open dialog to change password"""
        self.current_password_input = AppTextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.current_password_input.clear_error()
        )
        self.new_password_input = AppTextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.new_password_input.clear_error()
        )
        self.confirm_password_input = AppTextField(
            label="Confirm New Password",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.confirm_password_input.clear_error()
        )

        self.change_password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Change Password"),
            inset_padding=ft.padding.all(20),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    height=250, 
                    controls=[
                        self.current_password_input,
                        self.new_password_input,
                        self.confirm_password_input,
                    ],
                )
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.change_password_dialog)),
                ft.TextButton("Update", on_click=lambda e: self.page.run_task(self.update_password_task))
            ]
        )
        self.page.open(self.change_password_dialog)

    async def update_password_task(self):
        """Validate and update password"""
        current_password = self.current_password_input.value.strip()
        new_password = self.new_password_input.value.strip()
        confirm_password = self.confirm_password_input.value.strip()

        # Validate inputs
        is_valid, errors = validate_password_change(current_password, new_password, confirm_password)
        if not is_valid:
            self.current_password_input.error_text = errors.get("current_password", "")
            self.new_password_input.error_text = errors.get("new_password", "")
            self.confirm_password_input.error_text = errors.get("confirm_password", "")
            self.page.update()
            return
        
        user_id = self.user.get("id")
        # Verify current password
        self.change_password_dialog.actions[0].disabled = True
        self.change_password_dialog.actions.pop()
        self.change_password_dialog.actions.append(ft.Container(ft.ProgressRing(width=8, height=8)))
        self.change_password_dialog.update()
        verify_response = await verify_user_password(user_id, current_password)
        
        self.change_password_dialog.actions.pop()
        self.change_password_dialog.actions.append(ft.TextButton("Save", on_click=lambda e: self.page.run_task(self.update_password_task)))
        self.change_password_dialog.actions[0].disabled = False
        self.change_password_dialog.update()

        if not verify_response.get("success"):
            self.current_password_input.error_text = "Incorrect current password"
            self.page.update()
            return
        
        # Password verified, proceed to update
        self.password_to_update = new_password

    def save_profile_changes(self, e):
        self.user["first_name"] = self.first_name_input.value
        self.user["last_name"] = self.last_name_input.value

        # Save to client_storage or database
        self.page.client_storage.remove("user_info")
        self.page.client_storage.set("user_info", self.user)
        self.page.run_task(self._update_profile_task)

        print("Profile updated:", self.user)

    async def _update_profile_task(self):
        response = await update_profile(self.user, self.password_to_update if hasattr(self, 'password_to_update') else None)

        if response.get("success"):
            print("Profile successfully updated on server.")
            self.user_full_name = f"{self.user['first_name']} {self.user['last_name']}".strip()
            self.full_name_text.value = self.user_full_name
            self.page.update()
        else:
            print("Failed to update profile on server.")


    def delete_account(self, e):
        """Handle account deletion"""
        self.delete_dialog = ft.AlertDialog(
            title=ft.Text("Delete Account"),
            content=ft.Text("Are you sure you want to delete your account? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.delete_dialog)),
                ft.TextButton(
                    "Delete",
                    on_click=lambda e: self.page.run_task(self.confirm_delete_account),
                ),
            ]
        )
        self.page.open(self.delete_dialog)

    async def confirm_delete_account(self):
        """Confirm account deletion after password input"""
        self.page.close(self.delete_dialog)

        self.password_textfield = AppTextField(
            label="Enter your password to confirm",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.password_textfield.clear_error()
        )

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Container(
                ft.Column(
                    height=150, 
                    controls=[
                        ft.Text("Please enter your password to confirm account deletion:"),
                        self.password_textfield
                    ],
                )
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(confirm_dialog)),
                ft.TextButton(
                    "Delete",
                    on_click=lambda e: self.page.run_task(self._delete_account_task),
                ),
            ]
        )
        self.page.open(confirm_dialog)

    async def _delete_account_task(self):
        password = self.password_textfield.value.strip()
        user_id = self.user.get("id")

        if not password:
            self.password_textfield.error_text = "Password cannot be empty"
            self.page.update()
            return

        response = await delete_account(user_id, password)
        if response.get("success"):
            print("Account deleted successfully.")
            self.page.go("/logout")
        else:
            self.password_textfield.error_text = "Incorrect password. Please try again."
            self.page.update()


    async def download_pdf(self):
        """Download user data as PDF"""
        from config import Config
        # import httpx
        user_id = self.user.get("id")
        api_base_url = Config.API_BASE_URL
        download_url = f"{api_base_url}/profile/download_data/{user_id}"

        self.page.launch_url(download_url)

        # async with httpx.AsyncClient() as client:
        #     response = await client.get(download_url)

        # if response.status_code != 200:
        #     return

        # path = Path("C:/Users/Admin/Downloads/user_data.pdf")
        # path.write_bytes(response.content)

        # self.page.launch_url(path.as_uri())