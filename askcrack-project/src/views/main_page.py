import flet as ft
from .template import TemplatePage


class MainPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build(self) -> ft.View:
        """Build the main page UI"""

        # Toggle theme button
        self.toggle_theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE if self.is_light else ft.Icons.DARK_MODE,
            width=50,
            on_click=self.toggle_theme
        )

        # Drawer header with title and theme toggle
        self.drawer_header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Cracktify", size=20, weight="bold"),
                    self.toggle_theme_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(16, 10, 16, 10),    
        )

        # Drawer
        self.drawer = ft.NavigationDrawer(
            on_change=self.on_drawer_change,
            controls=[
                self.drawer_header,

                ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationDrawerDestination(icon=ft.Icons.GROUP, label="Groups"),
                ft.NavigationDrawerDestination(icon=ft.Icons.IMAGE, label="Gallery"),
                ft.NavigationDrawerDestination(icon=ft.Icons.HISTORY, label="Detection History"),
                ft.NavigationDrawerDestination(icon=ft.Icons.ASSESSMENT, label="Reports"),
                ft.Divider(leading_indent=25, trailing_indent=25),

                # Admin-only
                ft.NavigationDrawerDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Admin Dashboard"),

                ft.Divider(leading_indent=25, trailing_indent=25),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS, label="Settings"),
                ft.NavigationDrawerDestination(icon=ft.Icons.INFO, label="About"),
                ft.NavigationDrawerDestination(icon=ft.Icons.HELP, label="Help"),
            ]
        )

        # App Bar
        self.appbar = ft.AppBar(
            # automatically_imply_leading=False,
            toolbar_height=60,
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: self.page.open(self.drawer)
            ),
            title=ft.Container(
                content=ft.Text("Home", size=18, weight="bold"),
            ),
            center_title=False,
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
        
        # Animation for FABs
        self.anim = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT_QUINT)

        # Floating action buttons for detection
        self.action_buttons = ft.Column(
            [
                ft.ElevatedButton(
                    icon=ft.Icons.CAMERA_ALT,
                    text="Live Detection",
                    style=ft.ButtonStyle(
                        shape=ft.StadiumBorder(),
                        padding=ft.padding.all(15),
                    ),
                    on_click=lambda e: print("Camera Detection")
                ),
                ft.ElevatedButton(
                    icon=ft.Icons.IMAGE,
                    text="Upload Image",
                    style=ft.ButtonStyle(
                        shape=ft.StadiumBorder(),
                        padding=ft.padding.all(15),
                    ),
                    on_click=lambda e: print("Image Detection")
                ),
            ],
            spacing=10,
            visible=False,
            horizontal_alignment=ft.CrossAxisAlignment.END,

        )

        # Main FAB
        self.detect_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,  
            text="New Detection",
            mini=False,
            animate_size=self.anim,
            on_click=self.open_detect_menu,
        )

        # FAB container
        self.fab_container = ft.Column(
            controls=[
                self.action_buttons,
                self.detect_button,
            ],
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            spacing=10,
        )

        # Main body content
        self.body_content = ft.Container(
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text("Welcome to Cracktify!", size=24, weight="bold"),
                    ft.Text("Your all-in-one solution for crack detection and analysis.", size=16),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor=ft.Colors.WHITE if self.is_light else ft.Colors.BLACK87,
            alignment=ft.alignment.center,

        )
        
        return self.layout(
            content=[self.body_content],
            appbar=self.appbar,
            drawer=self.drawer,
            floating_action_button=self.fab_container,
        )
    
    def toggle_theme(self, e):
        """Toggle between light and dark themes"""
        current_theme = self.page.theme_mode

        if current_theme == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.toggle_theme_button.icon = ft.Icons.DARK_MODE

        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.toggle_theme_button.icon = ft.Icons.LIGHT_MODE

        # Determine actual brightness if using SYSTEM
        # if current_mode == ft.ThemeMode.SYSTEM:
        #     is_light = self.page.platform_brightness == ft.Brightness.LIGHT
        # else:
        #     is_light = current_mode == ft.ThemeMode.LIGHT

        # Toggle logic
        # if is_light:
        #     self.page.theme_mode = ft.ThemeMode.DARK
        # else:
        #     self.page.theme_mode = ft.ThemeMode.LIGHT
    
        self.page.update()

    def open_detect_menu(self, e):
        """Open detection action buttons menu"""
        opened = not self.action_buttons.visible

        if opened:
            # Open menu
            self.action_buttons.visible = True
            self.detect_button.icon = ft.Icons.CLOSE
            self.detect_button.text = "Close"
        else:
            # Close menu
            self.action_buttons.visible = False
            self.detect_button.icon = ft.Icons.ADD
            self.detect_button.text = "New Detection"

        self.page.update()

    def on_drawer_change(self, e):
        """Handle drawer navigation changes"""
        # TODO: Close drawer on change when opened by swipe

        selected_index = self.drawer.selected_index # Get selected index

        # Update page title and content based on selection
        match selected_index:
            case 0: self.show_home()
            case 1: self.show_groups()
            case 2: self.show_gallery()
            case 3: self.show_detection_history()
            case 4: self.show_reports()
            case 5: self.show_admin_dashboard()
            case 6: self.show_settings()
            case 7: self.show_about()
            case 8: self.show_help()
            case _: pass

        # Close drawer
        self.drawer.open = False
        self.page.update()

    def show_home(self):
        """Handle Home navigation"""
        self.appbar.title.content.value = "Home"
        self.body_content.content.controls = [
            ft.Text("Welcome to Cracktify!", size=24, weight="bold"),
            ft.Text("Your all-in-one solution for crack detection and analysis.", size=16),
        ]

    def show_groups(self):
        """Handle Groups navigation"""
        self.appbar.title.content.value = "Groups"
        self.body_content.content.controls = [
            ft.Text("Groups Page", size=24, weight="bold"),
            ft.Text("Manage and view your groups here.", size=16),
        ]

    def show_gallery(self):
        """Handle Gallery navigation"""
        self.appbar.title.content.value = "Gallery"
        self.body_content.content.controls = [
            ft.Text("Gallery Page", size=24, weight="bold"),
            ft.Text("Browse detected cracks and images here.", size=16),
        ]

    def show_detection_history(self):
        """Handle Detection History navigation"""
        self.appbar.title.content.value = "Detection History"
        self.body_content.content.controls = [
            ft.Text("Detection History Page", size=24, weight="bold"),
            ft.Text("View your past detection records here.", size=16),
        ]
    
    def show_reports(self):
        """Handle Reports navigation"""
        self.appbar.title.content.value = "Reports"
        self.body_content.content.controls = [
            ft.Text("Reports Page", size=24, weight="bold"),
            ft.Text("Generate and view reports here.", size=16),
        ]

    def show_admin_dashboard(self):
        """Handle Admin Dashboard navigation"""
        self.appbar.title.content.value = "Admin Dashboard"
        self.body_content.content.controls = [
            ft.Text("Admin Dashboard Page", size=24, weight="bold"),
            ft.Text("Administrative tools and settings.", size=16),
        ]

    def show_settings(self):
        """Handle Settings navigation"""
        self.appbar.title.content.value = "Settings"
        self.body_content.content.controls = [
            ft.Text("Settings Page", size=24, weight="bold"),
            ft.Text("Adjust your application settings here.", size=16),
        ]

    def show_about(self):
        """Handle About navigation"""
        self.appbar.title.content.value = "About"
        self.body_content.content.controls = [
            ft.Text("About Page", size=24, weight="bold"),
            ft.Text("Information about the Cracktify application.", size=16),
        ]

    def show_help(self):
        """Handle Help navigation"""
        self.appbar.title.content.value = "Help"
        self.body_content.content.controls = [
            ft.Text("Help Page", size=24, weight="bold"),
            ft.Text("Get assistance and support here.", size=16),
        ]                   

    def show_detect(self, e):
        """Handle New Detection action"""
        print("New Detection initiated")