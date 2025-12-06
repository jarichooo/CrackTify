import flet as ft

from widgets.inputs import AppTextField
from widgets.buttons import PrimaryButton, SecondaryButton, CustomTextButton
from services.profile_service import update_profile
from utils.image_utils import image_to_base64

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
        # ----------------------------

    def build(self) -> ft.Control:
        """Build the profile page UI"""
        self.profile_image_path = self.user.get("avatar_url") or "https://www.w3schools.com/howto/img_avatar.png"
        self.user_first_name = self.user.get("first_name")
        self.user_last_name = self.user.get("last_name")
        self.full_name = f"{self.user_first_name} {self.user_last_name}"
        self.user_email = self.user.get("email", "")

        # FilePicker for avatar
        avatar_picker = ft.FilePicker(on_result=self.on_avatar_picked)
        self.page.overlay.append(avatar_picker)

        self.avatar_control = ft.Stack(
            controls=[
                ft.CircleAvatar(foreground_image_src=self.profile_image_path, radius=50),
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

        def allow_email_change(e):
            self.email_input.read_only = False
            self.email_input.focus()
            self.page.update()

        self.email_input = AppTextField(
            label="Email",
            border=ft.InputBorder.UNDERLINE,
            value=self.user_email,
            suffix_icon=ft.IconButton(icon=ft.Icons.EDIT, on_click=allow_email_change),
            read_only=True,
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

    def on_avatar_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        avatar_path = e.files[0].path
        avatar_base64 = image_to_base64(avatar_path)
        self.user["avatar"] = avatar_base64  # update user dictionary

        # Update CircleAvatar (left untouched)
        self.avatar_control
        self.body_content.content.controls[0].controls[0].src = avatar_path
        self.body_content.content.controls[0].controls[0].update()

    def save_profile_changes(self, e):
        self.user["first_name"] = self.first_name_input.value
        self.user["last_name"] = self.last_name_input.value
        self.user["email"] = self.email_input.value

        # Save to client_storage or database
        self.page.client_storage.set("user", self.user)

        print("Profile updated:", self.user)
