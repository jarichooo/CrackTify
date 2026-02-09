import json
import flet as ft

from .template import TemplatePage
from .edit_user_page import EditUserPage

from widgets.buttons import PrimaryButton, SecondaryButton
from widgets.inputs import TextField

from services.profile_service import verify_user_password, update_profile, delete_account
from services.otp_service import send_otp, verify_otp

from utils.input_validation import validate_password_change

class MorePage(TemplatePage):
    def __init__(self, page: ft.Page, user):
        super().__init__(page)
        self.user = user

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
                                        ft.PopupMenuItem(content="Light",), # on_click=handle_theme_mode
                                        ft.PopupMenuItem(content="Dark",),
                                        ft.PopupMenuItem(content="System",),
                                    ],
                                )
                            ),
                            ft.ListTile(
                                title=ft.Text("Theme Color"),
                                trailing=ft.PopupMenuButton(
                                    icon=ft.Icons.ARROW_DROP_DOWN,
                                    items=[
                                        ft.PopupMenuItem(content="Red",), # on_click=handle_theme_color
                                        ft.PopupMenuItem(content="Blue",),
                                        ft.PopupMenuItem(content="Green",),
                                        ft.PopupMenuItem(content="Yellow",),
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
                                on_click=lambda _: print("Hello world")
                            ),
                            ft.ListTile(
                                title=ft.Text("Delete Account", color=ft.Colors.RED),
                                # on_click=self.delete_account,
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
                    # on_click=lambda _: self.about_click
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

    def refresh_user(self, updated_user):
        self.user = updated_user

        # Update the controls directly
        self.name_text.value = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        self.email_text.value = self.user.get("email_address", "no email")
        self.avatar_image.content.src = self.user.get("avatar_url", "")

        self.page.update()
        
    async def on_infos_click(self, e):
        edit_page = EditUserPage(
            self.page, 
            self.user,
            on_save=lambda updated_user: self.refresh_user(updated_user)
        )
        self.page.views.append(edit_page.build())

    async def on_logout_click(self, e):
        await self.page.shared_preferences.remove("auth_token")
        await self.page.shared_preferences.remove("user")
        await self.page.push_route("/login")
