import build
import flet as ft
import os
import shutil
from datetime import datetime
from pathlib import Path

from widgets.inputs import AppTextField
from widgets.buttons import PrimaryButton, SecondaryButton, CustomTextButton
from services.profile_service import update_profile
from services.otp_service import send_otp, verify_otp
from utils.image_utils import image_to_base64, base64_to_image

class ProfilePage:
    def __init__(self, page: ft.Page):
        self.page = page

        self.user = self.page.client_storage.get("user_info")  # Load user data from client storage

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
        self.profile_image_base64 = self.user.get("avatar_base64")
        self.profile_image_path = base64_to_image(self.profile_image_base64, f"{self.user.get('id')}.png") if self.profile_image_base64 else None
        self.user_first_name = self.user.get("first_name")
        self.user_last_name = self.user.get("last_name")
        self.full_name = f"{self.user_first_name} {self.user_last_name}"
        self.user_email = self.user.get("email", "")

        # FilePicker for avatar
        avatar_picker = ft.FilePicker(on_result=self.on_avatar_picked)
        self.page.overlay.append(avatar_picker)

        self.avatar_image = ft.CircleAvatar(
            foreground_image_src=self.profile_image_path, 
            background_image_src="https://www.w3schools.com/howto/img_avatar.png",
            radius=50
        )

        self.avatar_control = ft.Stack(
            controls=[
                self.avatar_image,  # store reference for updating
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

        self.email_input = AppTextField(
            label="Email",
            border=ft.InputBorder.UNDERLINE,
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
                                on_click=lambda e: print("Change Password clicked")
                            ),
                            ft.ListTile(
                                title=ft.Text("Two-Factor Authentication"),
                                trailing=ft.Switch(value=False),
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
                                on_click=lambda e: print("Download My Data clicked")
                            ),
                            ft.ListTile(
                                title=ft.Text("Delete My Account", color=ft.Colors.RED_100),
                                on_click=lambda e: print("Delete My Account clicked"),
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
            ft.Text(self.full_name, size=20, weight="bold"),
            ft.Divider(height=15, opacity=0),
            self.list_view,
        ]
    
    def allow_email_change(self, e):
        """Enable email input for editing and send OTP"""
        self.email_input.read_only = False
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

        # Create assets folder if not exists
        assets_dir = Path(__file__).parent.parent.parent.parent / "src" / "assets" / "avatars"
        os.makedirs(assets_dir, exist_ok=True)

        # Save file with unique name
        ext = os.path.splitext(avatar_path)[1]
        filename = f"user_{self.user.get('id', 'unknown')}{ext}"  # you can add timestamp if you want
        dest_path = assets_dir / filename
        shutil.copy2(avatar_path, dest_path)

        # Update CircleAvatar
        # TODO: Fix image not updating issue
        self.avatar_image.foreground_image_src = dest_path
        self.page.update()

        print(f"Avatar saved to assets: {dest_path}")

    def save_profile_changes(self, e):
        self.user["first_name"] = self.first_name_input.value
        self.user["last_name"] = self.last_name_input.value
        self.user["email"] = self.new_email if self.new_email else self.user_email.value

        # Save to client_storage or database
        self.page.client_storage.set("user_info", self.user)
        self.page.run_task(self._update_profile_task)

        print("Profile updated:", self.user)

    async def _update_profile_task(self):
        response = await update_profile(self.user)

        if response.get("success"):
            print("Profile successfully updated on server.")
            self.build()
            self.page.update()
        else:
            print("Failed to update profile on server.")