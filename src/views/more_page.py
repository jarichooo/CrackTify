import flet as ft

from .template import TemplatePage

from widgets.buttons import PrimaryButton, SecondaryButton
from widgets.inputs import TextField

from services.profile_service import verify_user_password, update_profile, delete_account
from services.otp_service import send_otp, verify_otp
from utils.file_utils import image_to_base64, base64_to_image
from utils.input_validation import validate_password_change

class MorePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        saved_theme_mode = self.page.shared_preferences.get("theme_mode")
        if saved_theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif saved_theme_mode == "system":
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        saved_theme_color = self.page.shared_preferences.get("theme_color")
        if saved_theme_color:
            color_map = {
                "red": ft.Colors.RED,
                "blue": ft.Colors.BLUE,
                "green": ft.Colors.GREEN,
                "yellow": ft.Colors.YELLOW,
            }
            chosen = color_map.get(saved_theme_color, ft.Colors.BLUE)
            self.page.theme = ft.Theme(color_scheme_seed=chosen)

        self.new_email = None  # To store new email during change process

    def build(self) -> ft.View:
        app_bar = ft.AppBar(
            automatically_imply_leading=True,
        )

        # self.user = self.page.shared_preferences.get("user_info")  # Load user data from client storage
        # self.user_first_name = self.user.get("first_name", "")
        # self.user_last_name = self.user.get("last_name", "")
        # self.user_email = self.user.get("email", "")
        # self.user_avatar_base64 = self.user.get("avatar_base64", "")

        self.user_first_name = "John"
        self.user_last_name = "Doe"
        self.user_email = "john.doe@example.com"
        self.user_avatar_base64 = None

        self.full_name = f"{self.user_first_name} {self.user_last_name}".strip()

        self.avatar_image = ft.Container(
            width=100,
            height=100,
            border_radius=50,
            bgcolor=ft.Colors.GREY_300,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=self.on_avatar_click,
            content=ft.Image(
                src=self.user_avatar_base64 if self.user_avatar_base64 else "https://www.gravatar.com/avatar/?d=mp&s=200",
                fit=ft.BoxFit.COVER,
            )
        )

        # Editable Fields
        self.first_name_input = TextField(
            label="First Name",
            border=ft.InputBorder.UNDERLINE,
            value=self.user_first_name,
            expand=1
        )
        self.last_name_input = TextField(
            label="Last Name",
            border=ft.InputBorder.UNDERLINE,
            value=self.user_last_name,
            expand=1
        )

        self.full_name_text = ft.Text(self.full_name, size=20, weight="bold")

        self.email_input = TextField(
            label="Email",
            border=ft.InputBorder.NONE,
            value=self.user_email,
            suffix_icon=ft.IconButton(icon=ft.Icons.EDIT, on_click=self.allow_email_change),
            read_only=True,
        )

        self.otp_input = TextField(
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

        self.panel_list = ft.ExpansionPanelList(
            elevation=0,
            divider_color=ft.Colors.TRANSPARENT,
            controls=[
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Account Information", weight="bold", size=16),
                        alignment=ft.Alignment.CENTER_LEFT,
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
                        alignment=ft.Alignment.CENTER_LEFT,
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
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Theme Mode"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(text="Light", on_click=self.handle_theme_mode),
                                        ft.PopupMenuItem(text="Dark", on_click=self.handle_theme_mode),
                                        ft.PopupMenuItem(text="System", on_click=self.handle_theme_mode),
                                    ],
                                )
                            ),
                            ft.ListTile(
                                title=ft.Text("Theme Color"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(text="Red", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(text="Blue", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(text="Green", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(text="Yellow", on_click=self.handle_theme_color),
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
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.START,
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Download My Data"),
                                on_click=lambda e: self.page.run_task(self.download_pdf),
                            ),
                            ft.ListTile(
                                title=ft.Text("Delete My Account", color=ft.Colors.RED),
                                on_click=self.delete_account,
                            ),
                        ],
                        tight=True,
                    ),
                ),

            ]
        )

        return self.layout(
            route="/more",
            appbar=app_bar,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                
                self.avatar_image,
                self.full_name_text,
                ft.ListView(
                    expand=True,
                    controls=[self.panel_list, button_column],
                )
            ]
        )
    
    def handle_theme_mode(self, e):
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
        self.page.shared_preferences.set("theme_mode", mode_str)
        self.page.update()

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

    def allow_email_change(self, e):
        """Enable email input for editing and send OTP"""
        self.email_input.read_only = False
        self.email_input.border = ft.InputBorder.UNDERLINE
        self.email_input.focus()
        
        # Create new OTP input for each attempt
        self.otp_input = TextField(
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


    def save_profile_changes(self, e):
        self.user["first_name"] = self.first_name_input.value
        self.user["last_name"] = self.last_name_input.value

        # Save to shared_preferences or database
        self.page.shared_preferences.remove("user_info")
        self.page.shared_preferences.set("user_info", self.user)
        self.page.run_task(self._update_profile_task)

        print("Profile updated:", self.user)
    
    def open_change_password_dialog(self, e):
        """Open dialog to change password"""
        self.current_password_input = TextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.current_password_input.clear_error()
        )
        self.new_password_input = TextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            on_change= lambda e: self.new_password_input.clear_error()
        )
        self.confirm_password_input = TextField(
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

    async def _update_profile_task(self):
        response = await update_profile(self.user, self.password_to_update if hasattr(self, 'password_to_update') else None)

        if response.get("success"):
            print("Profile successfully updated on server.")
            self.user_full_name = f"{self.user['first_name']} {self.user['last_name']}".strip()
            self.full_name_text.value = self.user_full_name
            self.page.update()
        else:
            print("Failed to update profile on server.")