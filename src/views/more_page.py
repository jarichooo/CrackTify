import asyncio
import json
import flet as ft

from .template import TemplatePage
from .edit_user_page import EditUserPage

from widgets.inputs import TextField
from widgets.dialogs import AlertDialog

from services.profile_service import (
    verify_user_password,
    update_password,
    delete_account,
)
from model.user import User


class MorePage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.user = User.to_dict()  # Convert the user dict to a User instance

        self.saved_theme_mode = None
        self.saved_theme_color = None

        asyncio.create_task(self.get_theme_mode())
        asyncio.create_task(self.get_theme_color())

    async def get_theme_mode(self):
        self.saved_theme_mode = await self.page.shared_preferences.get("theme_mode")

    async def get_theme_color(self):
        self.saved_theme_color = await self.page.shared_preferences.get("theme_color")

    def build(self) -> ft.View:
        app_bar = ft.AppBar(
            title=ft.Text("Settings"),
            force_material_transparency=True,
        )

        # Avatar Image control
        self.avatar_image = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        width=120,
                        height=120,
                        border_radius=100,
                        bgcolor=ft.Colors.GREY_300,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src=self.user.get("avatar_url", ""),
                            fit=ft.BoxFit.COVER,
                        ),
                    ),
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.EDIT, size=15, color=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        width=20,
                        height=20,
                        bgcolor=ft.Colors.INVERSE_SURFACE,
                        border_radius=20,
                        alignment=ft.Alignment.CENTER,
                        on_click=self.on_infos_click,
                    ),
                ],
                alignment=ft.Alignment.BOTTOM_RIGHT,
            ),
            alignment=ft.Alignment.CENTER,
        )

        # Text controls for first & last name
        self.name_text = ft.Text(
            f"{self.user.get('first_name', 'first name')} {self.user.get('last_name', '')}",
            size=20,
            weight=ft.FontWeight.BOLD,
        )

        # Text control for email
        self.email_text = ft.Text(self.user.get("email_address", "no email"), size=16)

        self.user_info = ft.Container(
            on_click=self.on_infos_click,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[self.avatar_image, self.name_text, self.email_text],
            ),
        )

        self.menu = ft.Column(
            spacing=8,
            controls=[
                # Appearance Section
                ft.Text("Appearance", theme_style="titleSmall"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DARK_MODE_OUTLINED),
                    title=ft.Text("Theme Mode"),
                    trailing=ft.PopupMenuButton(
                        icon=ft.Icons.ARROW_DROP_DOWN,
                        items=[
                            ft.PopupMenuItem(
                                content="Light", on_click=self.handle_theme_mode
                            ),
                            ft.PopupMenuItem(
                                content="Dark", on_click=self.handle_theme_mode
                            ),
                            ft.PopupMenuItem(
                                content="System", on_click=self.handle_theme_mode
                            ),
                        ],
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.COLOR_LENS_OUTLINED),
                    title=ft.Text("Theme Color"),
                    trailing=ft.PopupMenuButton(
                        icon=ft.Icons.ARROW_DROP_DOWN,
                        items=[
                            ft.PopupMenuItem(
                                content="Red", on_click=self.handle_theme_color
                            ),
                            ft.PopupMenuItem(
                                content="Blue", on_click=self.handle_theme_color
                            ),
                            ft.PopupMenuItem(
                                content="Green", on_click=self.handle_theme_color
                            ),
                            ft.PopupMenuItem(
                                content="Yellow", on_click=self.handle_theme_color
                            ),
                        ],
                    ),
                ),
                ft.Divider(height=24),
                # Account & Security
                ft.Text("Account & Security", theme_style="titleSmall"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_OUTLINE),
                    title=ft.Text("Verify Engineer" if self.user.get("is_engineer") and not self.user.get("is_verified") else "Are you an engineer?"),
                    subtitle=ft.Text("Submit documentation to verify your status"),
                    on_click=self.verify_engineer_click,
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ASSIGNMENT_OUTLINE),
                    title=ft.Text("Assign an Engineer"),
                    subtitle=ft.Text("Assign an engineer to verify your detection results"),
                    on_click=self.assign_engineer_click,
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCK_OUTLINE),
                    title=ft.Text("Change Password"),
                    subtitle=ft.Text("Update your account password"),
                    on_click=self.change_password_click,
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE_OUTLINE, color=ft.Colors.RED),
                    title=ft.Text("Delete Account", color=ft.Colors.RED),
                    subtitle=ft.Text(
                        "This action cannot be undone",
                        color=ft.Colors.RED,
                    ),
                    on_click=self.delete_account,
                ),
                ft.Divider(height=24),
                # App Section
                ft.Text("App", theme_style="titleSmall"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                    title=ft.Text("About"),
                    subtitle=ft.Text("App version, developers, and repositories"),
                    on_click=self.show_about_dialog,
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                    title=ft.Text("Logout", color=ft.Colors.RED),
                    subtitle=ft.Text("Sign out of your account"),
                    on_click=self.on_logout_click,
                ),
            ],
        )
        return self.layout(
            route="/more",
            appbar=app_bar,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=20,
            controls=[
                self.user_info,  # User avatar with name and email
                ft.ListView(
                    expand=True,
                    controls=[self.menu],
                ),
            ],
        )

    def show_about_dialog(self, e):
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE),
                        ft.Text("About Cracktify", theme_style="titleLarge"),
                    ],
                ),
                content=ft.Container(
                    width=420,
                    height=400,
                    content=ft.Column(
                        spacing=18,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            # App Description
                            ft.Text(
                                "Cracktify helps users identify and understand wall crack issues "
                                "by providing accurate answers and guidance based on common "
                                "structural concerns.",
                                theme_style="bodyMedium",
                            ),
                            # Version
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.APP_SETTINGS_ALT_OUTLINED, size=18
                                    ),
                                    ft.Text("Version 2.0.0", theme_style="bodySmall"),
                                ],
                            ),
                            ft.Divider(),
                            # Academic Info
                            ft.Text("Academic Purpose", theme_style="titleMedium"),
                            ft.Text(
                                "This project was developed in partial fulfillment of the "
                                "requirements for the course:",
                                theme_style="bodyMedium",
                            ),
                            ft.Text(
                                "• Software Engineering 2",
                                theme_style="bodySmall",
                            ),
                            ft.Divider(),
                            # Repositories
                            ft.Text("Project Repositories", theme_style="titleMedium"),
                            ft.Column(
                                spacing=3,
                                controls=[
                                    ft.TextButton(
                                        content="Cracktify App (Frontend)",
                                        icon=ft.Icons.OPEN_IN_NEW,
                                        on_click=lambda e: asyncio.create_task(
                                            self.page.launch_url(
                                                "https://github.com/jarichooo/CrackTify"
                                            )
                                        ),
                                    ),
                                    ft.TextButton(
                                        content="Cracktify Server (Backend)",
                                        icon=ft.Icons.OPEN_IN_NEW,
                                        on_click=lambda e: asyncio.create_task(
                                            self.page.launch_url(
                                                "https://github.com/ven-62/cracktify-server"
                                            )
                                        ),
                                    ),
                                ],
                            ),
                            ft.Divider(),
                            # Developers
                            ft.Text("Developers", theme_style="titleMedium"),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.TextButton(
                                        content="John Louie Bagaporo",
                                        on_click=lambda e: asyncio.create_task(
                                            self.page.launch_url(
                                                "https://github.com/johnlouie2004"
                                            )
                                        ),
                                    ),
                                    ft.TextButton(
                                        content="Joshua Jericho Barja",
                                        on_click=lambda e: asyncio.create_task(
                                            self.page.launch_url(
                                                "https://github.com/jarichooo"
                                            )
                                        ),
                                    ),
                                    ft.TextButton(
                                        content="Ven John Rey Lavapie",
                                        on_click=lambda e: asyncio.create_task(
                                            self.page.launch_url(
                                                "https://github.com/ven-62"
                                            )
                                        ),
                                    ),
                                ],
                            ),
                            ft.Divider(),
                            # Contact
                            ft.Text("Contact / Support", theme_style="titleMedium"),
                            ft.Text(
                                "cracktify.noreply@gmail.com",
                                theme_style="bodySmall",
                            ),
                        ],
                    ),
                ),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda _: self.page.pop_dialog(),
                    )
                ],
            )
        )

    def handle_theme_mode(self, e):
        selected_mode = e.control.content.lower()
        self.page.theme_mode = selected_mode.lower()
        asyncio.create_task(
            self.page.shared_preferences.set("theme_mode", selected_mode.lower())
        )

    def handle_theme_color(self, e):
        selected_color = e.control.content.lower()
        color_map = {
            "red": ft.Colors.RED,
            "blue": ft.Colors.BLUE,
            "green": ft.Colors.GREEN,
            "yellow": ft.Colors.YELLOW,
        }
        chosen_color = color_map.get(selected_color, ft.Colors.BLUE)

        # Create a new theme with color seed
        self.page.theme = ft.Theme(color_scheme_seed=chosen_color)

        # Save selection
        asyncio.create_task(
            self.page.shared_preferences.set("theme_color", chosen_color.value)
        )  # Save the hex value of the color
        self.page.update()

    def refresh_user(self, updated_user):
        """Updates the user information displayed on the MorePage after editing."""
        self.user = updated_user

        # Update the controls directly
        self.name_text.value = (
            f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        )
        self.email_text.value = self.user.get("email_address", "no email")
        self.avatar_image.content.controls[0].content.src = self.user.get(
            "avatar_url", ""
        )

        self.page.update()

    async def on_infos_click(self, e):
        """Navigates to the EditUserPage when the user info section is clicked."""
        edit_page = EditUserPage(
            self.page,
            on_save=lambda updated_user: self.refresh_user(updated_user),
        )
        self.page.views.append(edit_page.build())

    async def verify_engineer_click(self, e):
        """Navigates to the VerifyEngineerPage when the verify engineer option is clicked."""
        if self.user.get("verified"):
            self.page.show_dialog(
                AlertDialog(
                    title="Already Verified",
                    content="Your engineer status has already been verified. Thank you!",
                    actions=[ft.TextButton("OK", on_click=lambda e: (
                        setattr(self.page.dialog, "open", False), self.page.update()
                    ))],
                )
            )
            return
        
        from .verify_engineer import VerifyEngineerPage

        verify_page = VerifyEngineerPage(self.page)
        self.page.views.append(verify_page.build())

    def change_password_click(self, e):
        """Open dialog to change password."""
        self.cp_field = TextField(
            label="Current Password", value="", password=True, can_reveal_password=True
        )
        self.np_field = TextField(
            label="New Password", password=True, can_reveal_password=True
        )
        self.cnp_field = TextField(
            label="Confirm New Password", password=True, can_reveal_password=True
        )

        self.cp_dialog = AlertDialog(
            title="Change Password",
            modal=True,
            content=ft.Column(
                height=270,
                controls=[
                    ft.Text(
                        "Please enter your current password and the new password you want to set."
                    ),
                    self.cp_field,
                    self.np_field,
                    self.cnp_field,
                ],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton(
                    "Change",
                    on_click=lambda _: self.page.run_task(self.change_password),
                ),
            ],
        )

        self.page.show_dialog(self.cp_dialog)

    async def change_password(self):
        # Here you would call the change_password service with the current and new passwords and handle the response
        from utils.input_validation import validate_password_change

        # Validate inputs before making API call
        is_valid, error = validate_password_change(
            self.cp_field.value, self.np_field.value, self.cnp_field.value
        )

        # If validation fails, show errors and return early
        if not is_valid:
            self.cp_field.error = error.get("current_password", None)
            self.np_field.error = error.get("new_password", None)
            self.cnp_field.error = error.get("confirm_password", None)
            self.page.update()
            return

        self.cp_dialog.actions[1] = ft.ProgressRing()
        self.page.update()

        # Verify user current password
        verify_resp = await verify_user_password(
            self.user.get("id"), self.cp_field.value
        )

        # If current password doesnt match, return an error
        if not verify_resp.get("success"):
            self.cp_field.error = verify_resp.get("error", "An error occurred")
            self.page.update()
            return

        # # Update user password
        resp = await update_password(self.user.get("id"), self.cnp_field.value)

        # If there's an error while updating password, return an error
        if not resp.get("success"):
            self.cp_field.error = resp.get("error", "An error occurred")
            self.cp_dialog.actions[1] = ft.TextButton(
                "Change", on_click=lambda _: self.page.run_task(self.change_password)
            )
            self.page.update()
            return

        self.page.pop_dialog()
        self.page.show_dialog(
            AlertDialog(
                title="Password Changed",
                content="Your password has been successfully changed.",
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())
                ],
            )
        )

    async def on_logout_click(self, e):
        """Shows a confirmation dialog before logging out."""
        self.page.show_dialog(
            AlertDialog(
                title="Confirm Logout",
                content="Are you sure you want to log out?",
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                    ft.TextButton(
                        "Logout",
                        style=ft.ButtonStyle(color=ft.Colors.RED),
                        on_click=lambda _: self.page.run_task(self.confirm_logout),
                    ),
                ],
            )
        )

    async def confirm_logout(self):
        await self.page.shared_preferences.remove("auth_token")
        await self.page.shared_preferences.remove("user")
        await self.page.push_route("/login")

    async def delete_account(self, e):
        """Shows a confirmation dialog before deleting the account."""
        self.page.show_dialog(
            AlertDialog(
                title="Confirm Account Deletion",
                content="Are you sure you want to delete your account? This action cannot be undone.",
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                    ft.TextButton(
                        "Delete",
                        style=ft.ButtonStyle(color=ft.Colors.RED),
                        on_click=lambda _: asyncio.create_task(confirm_delete()),
                    ),
                ],
            )
        )

        async def confirm_delete():
            # Here you would call the delete_account service and handle the response
            self.password_field = TextField(
                label="Enter your password to confirm",
                password=True,
                can_reveal_password=True,
                value="",
            )
            self.page.pop_dialog()  # Close the previous confirmation dialog
            self.page.show_dialog(
                AlertDialog(
                    title="Confirm Password",
                    content=ft.Column(
                        height=120,
                        controls=[
                            ft.Text(
                                "Please enter your password to confirm account deletion."
                            ),
                            self.password_field,
                        ],
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancel", on_click=lambda _: self.page.pop_dialog()
                        ),
                        ft.TextButton(
                            "Delete",
                            style=ft.ButtonStyle(color=ft.Colors.RED),
                            on_click=lambda _: asyncio.create_task(
                                confirm_password(self.password_field.value)
                            ),
                        ),
                    ],
                )
            )

            async def confirm_password(password):
                # Here you would call the delete_account service with the password and handle the response
                resp = await delete_account(self.user.get("id"), password)

                if not resp.get("success"):
                    self.password_field.error = resp.get("error", "An error occurred")
                    self.page.update()
                    return

                await self.page.shared_preferences.remove("auth_token")
                await self.page.shared_preferences.remove("user")

                self.page.show_dialog(
                    AlertDialog(
                        title="Account Deleted",
                        content="Your account has been successfully deleted.",
                        actions=[
                            ft.TextButton(
                                "OK",
                                on_click=lambda _: asyncio.create_task(
                                    self.page.push_route("/login")
                                ),
                            )
                        ],
                    )
                )
