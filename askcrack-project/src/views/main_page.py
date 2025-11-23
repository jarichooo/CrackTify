import flet as ft
from .template import TemplatePage


class MainPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        # Track selected bottom nav index
        self.selected_index = 0

    def build(self) -> ft.View:
        # DRAWER
        self.drawer = ft.NavigationDrawer(
            bgcolor=ft.Colors.BLACK87,
            controls=[
                # --- FIXED HEADER ---
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Cracktify", size=20, weight="bold", color=ft.Colors.WHITE),
                            ft.IconButton(icon=ft.Icons.LIGHT_MODE, width=50),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(16, 16, 16, 10),
                ),
                ft.NavigationDrawerDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationDrawerDestination(icon=ft.Icons.UPLOAD_FILE, label="Upload Image"),
                ft.NavigationDrawerDestination(icon=ft.Icons.PHOTO_LIBRARY, label="Gallery"),
                ft.NavigationDrawerDestination(icon=ft.Icons.HISTORY, label="History"),
                ft.NavigationDrawerDestination(icon=ft.Icons.PICTURE_AS_PDF, label="Reports"),

                ft.Divider(leading_indent=30, trailing_indent=30),

                ft.NavigationDrawerDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Admin Dashboard"),
                ft.NavigationDrawerDestination(icon=ft.Icons.PEOPLE, label="User Management"),
                ft.NavigationDrawerDestination(icon=ft.Icons.NOTIFICATIONS, label="Notifications"),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS, label="Settings"),

                ft.Divider(leading_indent=20, trailing_indent=20),

                ft.NavigationDrawerDestination(icon=ft.Icons.INFO, label="About"),
                ft.NavigationDrawerDestination(icon=ft.Icons.HELP, label="Help"),

            ]
        )

        # APP BAR
        self.appbar = ft.AppBar(
            bgcolor=ft.Colors.BLACK87,
            center_title=True,
            leading=ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=lambda e: self.page.open(self.drawer)
                ),
                padding=ft.padding.only(left=10)
            ),
            title=ft.Container(
                content=ft.Text("Home", size=20, weight="bold"),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            actions=[
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.PERSON,
                        tooltip="Profile",
                        on_click=lambda e: print("Go to profile")
                    ),
                    padding=ft.padding.only(right=10)
                )
            ]
        )

        # MAIN CONTENT
        self.body_content = ft.Column(
            expand=True,
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.camera_button = ft.FloatingActionButton(
            icon=ft.Icons.PHOTO_CAMERA,
            on_click=lambda _: print('Camera Clicked!')
        )

        return self.layout(
            content=[self.body_content],
            appbar=self.appbar,
            drawer=self.drawer,
            floating_action_button=self.camera_button
        )

  