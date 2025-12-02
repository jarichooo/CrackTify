import flet as ft
from .template import TemplatePage
from .pages import (
    about_page,
    admin_dashboard_page,
    detection_history_page,
    groups_page,
    help_page,
    home_page,
    reports_page,
    settings_page,
)
from .pages.gallery_page import ImageGallery

class MainPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.gallery_instance = ImageGallery(page)
        self.search_active = False

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

        # Normal title text
        self.normal_title = ft.Text("Home", size=18, weight="bold")

        # Search bar for gallery
        self.search_bar = ft.SearchBar(
            bar_hint_text="Search images...",
            view_elevation=0,
            divider_color="transparent",
            on_change=lambda e: self.on_gallery_search(e.control.value),
            height=40,
            expand=True,
            autofocus=True,
        )

        # Title container
        self.title_container = ft.Row(
            controls=[self.normal_title],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Search toggle button (icon swapped dynamically)
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip="Search",
            on_click=self.toggle_search,
        )

        # App Bar
        self.appbar = ft.AppBar(
            toolbar_height=60,
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: self.page.open(self.drawer)
            ),
            title=self.title_container,
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

        # Animation for FABs
        self.anim = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT_QUINT)

        # Main FAB
        self.detect_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,  
            text="New Detection",
            mini=True,
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
                controls=home_page.build(self.page),
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(left=20, right=20),
            expand=True,
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
        selected = self.drawer.selected_index

        # Map: index -> (title, page builder or instance)
        navigation_map = {
            0: ("Home", home_page.build),
            1: ("Groups", groups_page.build),
            2: ("Gallery", self.gallery_instance),  # already an instance
            3: ("Detection History", detection_history_page.build),
            4: ("Reports", reports_page.build),
            5: ("Admin Dashboard", admin_dashboard_page.build),
            6: ("Settings", settings_page.build),
            7: ("About", about_page.build),
            8: ("Help", help_page.build),
        }

        if selected in navigation_map:
            title, builder = navigation_map[selected]

            # If builder is an instance with build() method
            if hasattr(builder, "build") and callable(builder.build):
                self.show_content_page(title, lambda _: builder.build())
            else:
                # Function-based page
                self.show_content_page(title, builder)

        # Close drawer after selection
        self.drawer.open = False
        self.page.update()


    # Search Toggle Logic 
    def toggle_search(self, e):
        """Toggle search bar in AppBar for Gallery."""
        self.search_active = not self.search_active
        self.title_container.controls.clear()

        if self.search_active:
            # Show search bar
            self.title_container.controls.append(self.search_bar)
            self.search_button.icon = ft.Icons.CLOSE
        else:
            # Restore normal title
            self.title_container.controls.append(self.normal_title)
            self.search_button.icon = ft.Icons.SEARCH

            # Clear gallery filter if gallery is active
            if self.drawer.selected_index == 2 and hasattr(self.gallery_instance, "filter_images"):
                self.gallery_instance.filter_images("")

        self.page.update()

    # Called whenever user types text in SearchBar
    def on_gallery_search(self, query: str):
        """Filter images in gallery if gallery is active"""
        if self.drawer.selected_index == 2 and hasattr(self.gallery_instance, "filter_images"):
            self.gallery_instance.filter_images(query)

    # Navigation helper
    def show_content_page(self, title: str, content_builder: callable):
        self.normal_title.value = title

        # Reset title container
        self.title_container.controls.clear()
        self.title_container.controls.append(self.normal_title)
        self.search_active = False

        # Reset AppBar actions
        self.appbar.actions = []

        # Profile button
        profile_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.PERSON,
                tooltip="Profile",
                on_click=lambda e: print("Go to profile"),
            ),
            padding=ft.padding.only(right=10),
        )

        # Insert search only for Gallery
        if title == "Gallery":
            self.appbar.actions.append(self.search_button)

            # Restore search state if it was active before
            if self.search_active:
                self.title_container.controls.clear()
                self.title_container.controls.append(self.search_bar)
                self.search_button.icon = ft.Icons.CLOSE
            else:
                self.title_container.controls.clear()
                self.title_container.controls.append(self.normal_title)
                self.search_button.icon = ft.Icons.SEARCH

        self.appbar.actions.append(profile_btn)

        # Set page content
        self.body_content.content.controls = content_builder(self.page)
        self.page.update()

    def show_detect(self, e):
        """Handle New Detection action"""
        print("New Detection initiated")