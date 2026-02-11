import asyncio
import json
import flet as ft

from .template import TemplatePage
from .edit_user_page import EditUserPage

from widgets.buttons import PrimaryButton, SecondaryButton
from widgets.inputs import TextField
from widgets.dialogs import AlertDialog

from services.profile_service import verify_user_password, update_profile, update_password, delete_account
from services.otp_service import send_otp, verify_otp

from utils.input_validation import validate_password_change

class MorePage(TemplatePage):
    def __init__(self, page: ft.Page, user):
        super().__init__(page)
        self.user = user

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
            automatically_imply_leading=True,
        )

        # Avatar Image control
        self.avatar_image = ft.Container(
            width=150,
            height=150,
            border_radius=100,
            bgcolor=ft.Colors.GREY_300,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(
                src=self.user.get("avatar_url", ""),
                fit=ft.BoxFit.COVER,
            )
        )

        # Text controls for first & last name
        self.name_text = ft.Text(
            f"{self.user.get('first_name', 'first name')} {self.user.get('last_name', '')}",
            size=20,
            weight=ft.FontWeight.BOLD
        )

        # Text control for email
        self.email_text = ft.Text(
            self.user.get("email_address", "no email"),
            size=16
        )

        self.user_info = ft.Container(
            on_click=self.on_infos_click,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    self.avatar_image,
                    self.name_text,
                    self.email_text
                ]
            )
        )

        self.panel_list = ft.ExpansionPanelList(
            elevation=0,
            divider_color=ft.Colors.TRANSPARENT,
            controls=[
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Appearance", weight="bold", size=16),
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Theme Mode"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(content="Light", on_click=self.handle_theme_mode),
                                        ft.PopupMenuItem(content="Dark", on_click=self.handle_theme_mode),
                                        ft.PopupMenuItem(content="System", on_click=self.handle_theme_mode),
                                    ],
                                )
                            ),
                            ft.ListTile(
                                title=ft.Text("Theme Color"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(content="Red", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(content="Blue", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(content="Green", on_click=self.handle_theme_color),
                                        ft.PopupMenuItem(content="Yellow", on_click=self.handle_theme_color),
                                    ],
                                )
                            ),
                        ],
                        tight=True,
                    ),
                ),
                ft.ExpansionPanel(
                    header=ft.Container(
                        ft.Text("Security and Account", weight="bold", size=16),
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                title=ft.Text("Change Password"),
                                on_click=self.change_password_click, # Implement this method to navigate to the ChangePasswordPage
                            ),
                            ft.ListTile(
                                title=ft.Text("Delete Account", color=ft.Colors.RED),
                                on_click=self.delete_account,
                            ),
                        ],
                        tight=True,
                    ),
                )
            ]
        )

        self.button_column = ft.Column(
            controls=[
                ft.ListTile(
                    title=ft.Text("About"),
                    on_click=self.show_about_dialog,
                ),
                ft.ListTile(
                    title=ft.Text("Logout", color=ft.Colors.RED),
                    on_click=self.on_logout_click,
                ),
            ]
        )

        return self.layout(
            route="/more",
            appbar=app_bar,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=20,
            controls=[
                self.user_info, # User avatar with name and email
                ft.ListView(
                    expand=True,
                    controls=[self.panel_list, self.button_column],
                )
            ]
        )

    def show_about_dialog(self, e):
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("About CrackTify"),
                content=ft.ListView(
                    controls=[
                        # App Info
                        ft.Text(
                            "This application is designed to help users find answers to their questions, mainly cracks on walls related questions",

                        ),
                        ft.Divider(height=20, opacity=0),
                        ft.Text("App Version: 2.0.0", theme_style="bodySmall"),
                        ft.Divider(height=20, opacity=0),

                        # Academic Fulfillment
                        ft.Text("Project Fulfillment", theme_style="titleMedium"),
                        ft.Text(
                            "This project is developed in partial fulfillment of the requirements for the following courses:",
                            theme_style="bodyMedium",
                        ),
                        ft.Divider(height=5, opacity=0),
                        ft.Column(
                            controls=[
                                # ft.Text("🧑‍💻 Application Development and Emerging Technologies", theme_style="bodySmall"),
                                # ft.Text("🔐 Information Assurance and Security", theme_style="bodySmall"),
                                ft.Text("🧑‍💻 Software Engineering 2", theme_style="bodySmall"),
                            ],
                            spacing=2
                        ),

                        # Repository Link
                        ft.Divider(height=20, opacity=0),
                        ft.Text("CrackTify", theme_style="titleMedium"),
                        ft.TextButton(
                            content="View on GitHub 🔗",
                            icon=ft.Icons.LINK,
                            on_click=lambda e: asyncio.create_task(self.page.launch_url("https://github.com/jarichooo/CrackTify"))
                        ),

                        # Developers
                        ft.Divider(height=20, opacity=0),
                        ft.Text("Developers", theme_style="titleMedium"),
                        ft.Column(
                            controls=[
                                ft.TextButton(
                                    content="John Louie Bagaporo",
                                    on_click=lambda e: asyncio.create_task(self.page.launch_url("https://github.com/johnlouie2004"))
                                ),
                                ft.TextButton(
                                    content="Joshua Jericho Barja",
                                    on_click=lambda e: asyncio.create_task(self.page.launch_url("https://github.com/jarichooo"))
                                ),
                                ft.TextButton(
                                    content="Ven John Rey Lavapie",
                                    on_click=lambda e: asyncio.create_task(self.page.launch_url("https://github.com/ven-62"))
                                ),
                            ],
                            spacing=20
                        ),

                        # Contact
                        ft.Divider(height=20, opacity=0),
                        ft.Text("Contact / Support", theme_style="titleMedium"),
                        ft.Text("Email: cracktify.noreply@gmail.com", theme_style="bodySmall"),
                    ]
                ),
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.page.pop_dialog())
                ]
            )
        )


    def handle_theme_mode(self, e):
        selected_mode = e.control.content.lower()
        self.page.theme_mode = selected_mode.lower()
        asyncio.create_task(self.page.shared_preferences.set("theme_mode", selected_mode.lower()))

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
        self.page.theme = ft.Theme(
            color_scheme_seed=chosen_color
        )

        # Save selection
        asyncio.create_task(self.page.shared_preferences.set("theme_color", chosen_color.value)) # Save the hex value of the color
        self.page.update()


    def refresh_user(self, updated_user):
        """Updates the user information displayed on the MorePage after editing."""
        self.user = updated_user

        # Update the controls directly
        self.name_text.value = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        self.email_text.value = self.user.get("email_address", "no email")
        self.avatar_image.content.src = self.user.get("avatar_url", "")

        self.page.update()
        
    async def on_infos_click(self, e):
        """Navigates to the EditUserPage when the user info section is clicked."""
        edit_page = EditUserPage(
            self.page, 
            self.user,
            on_save=lambda updated_user: self.refresh_user(updated_user)
        )
        self.page.views.append(edit_page.build())

    def change_password_click(self, e):
        """Open dialog to change password."""
        self.cp_field = TextField(label="Current Password", password=True)
        self.np_field = TextField(label="New Password", password=True)
        self.cnp_field = TextField(label="Confirm New Password", password=True)

        self.cp_dialog = AlertDialog(
            title="Change Password",
            content=ft.Column(
                height=300,
                controls=[
                    ft.Text("Please enter your current password and the new password you want to set."),
                    self.cp_field,
                    self.np_field,
                    self.cnp_field
                ]
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton("Change", on_click=lambda _: self.page.run_task(self.change_password))    
            ]
        )

        self.page.show_dialog(
            self.cp_dialog
        )

    async def change_password(self):
        # Here you would call the change_password service with the current and new passwords and handle the response
        is_valid, error = validate_password_change(self.cp_field.value, self.np_field.value, self.cnp_field.value)

        if not is_valid:
            self.np_field.error = error["new_password"]
            self.cnp_field.error = error["confirm_new_password"]
            self.page.update()
            return

        self.cp_dialog.actions[1] = ft.ProgressRing()
        self.page.update()

        resp = await update_password(self.user.get("id"), self.cnp_field.value)

        if not resp.get("success"):
            self.cp_field.error = resp.get("message", "An error occurred")
            self.cp_dialog.actions[1] = ft.TextButton("Change", on_click=lambda _: self.page.run_task(self.change_password))  
            self.page.update()
            return

        self.page.pop_dialog()
        self.page.show_dialog(
            AlertDialog(
                title="Password Changed",
                content="Your password has been successfully changed.",
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())
                ]
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
                    ft.TextButton("Logout", on_click=lambda _: self.page.run_task(self.confirm_logout))
                ]
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
                    ft.TextButton("Delete", color=ft.Colors.RED, on_click=lambda _: asyncio.create_task(confirm_delete()))
                ]
            )
        )
        async def confirm_delete():
            # Here you would call the delete_account service and handle the response
            self.password_field = TextField(
                label="Enter your password to confirm", password=True
            )
            self.page.show_dialog(
                AlertDialog(
                    title="Confirm Password",
                    content=self.password_field,
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                        ft.TextButton("Delete", color=ft.Colors.RED, on_click=lambda _: asyncio.create_task(confirm_password(self.password_field.value)))
                    ]
                )
            )
            async def confirm_password(password):
                # Here you would call the delete_account service with the password and handle the response
                resp = await delete_account(self.user.get("id"), password)

                if not resp.get("success"):
                    self.password_field.error = resp.get("message", "An error occurred")
                    self.page.update()
                    return

                await self.page.shared_preferences.remove("auth_token")
                await self.page.shared_preferences.remove("user")

                self.page.show_dialog(
                    AlertDialog(
                        title="Account Deleted",
                        content="Your account has been successfully deleted.",
                        actions=[
                            ft.TextButton("OK", on_click=lambda _: asyncio.create_task(self.page.push_route("/login")))
                        ]
                    )
                )
