import time
import flet as ft
from .template import TemplatePage
from .pages import (
    ProfilePage, #
    HomePage,
    GroupsPage,#
    ImageGallery, #
    DetectionHistoryPage,
    ReportsPage,
    AboutPage
)
from utils.toggle_theme import toggle_theme
from widgets.inputs import AppTextField
from widgets.buttons import PrimaryButton, SecondaryButton, CustomTextButton

class MainPage(TemplatePage):
    """Main application page after login, with navigation and content areas."""
    def __init__(self, page: ft.Page):
        super().__init__(page)

        # Initialize page instances
        self.profile_instance = ProfilePage(page)
        self.home_instance = HomePage(page)
        self.groups_instance = GroupsPage(page)
        self.gallery_instance = ImageGallery(page)
        self.detection_history_instance = DetectionHistoryPage(page)
        self.reports_instance = ReportsPage(page)
        self.about_instance = AboutPage(page)

        self.search_active = False # Search bar state

        # Navigation map
        self.navigation_map = {
            0: ("Home", self.home_instance),
            1: ("Groups", self.groups_instance),
            2: ("Gallery", self.gallery_instance),
            3: ("Detection History", self.detection_history_instance),
            4: ("Reports", self.reports_instance),
            5: ("About", self.about_instance),
        }

        # Set initial view
        self.current_view_instance = self.home_instance
        self.current_title = "Home"

        self.user = self.page.client_storage.get("user_info")  # Load user data from client storage


    def build(self) -> ft.View:
        """Build the main page UI"""

        # Toggle theme button
        self.toggle_theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE if self.is_light else ft.Icons.DARK_MODE,
            width=50,
            on_click=lambda e: toggle_theme(e, self.page, self.toggle_theme_button)
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

                ft.NavigationDrawerDestination(icon=ft.Icons.INFO, label="About"),
            ]
        )

        # Normal title text
        self.normal_title = ft.Text(self.current_title, size=18, weight="bold")

        # Search bar for gallery
        self.search_bar = ft.SearchBar(
            bar_hint_text="Search...",
            view_elevation=0,
            divider_color="transparent",
            on_change=lambda e: self.on_search(e.control.value), # Call on_search method
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

        # Profile button
        self.profile_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_size=28,
                tooltip="Profile",
                on_click=self.open_profile,
            ),
            padding=ft.padding.only(right=10),
        )

        # Close profile button
        self.close_profile_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=28,
                tooltip="Close Profile",
                on_click=self.close_profile,
            ),
            padding=ft.padding.only(right=10),
        )

        # Drawer button
        self.drawer_button = ft.IconButton(
            icon=ft.Icons.MENU,
            on_click=lambda e: self.page.open(self.drawer),
        )

        # App Bar
        self.appbar = ft.AppBar(
            toolbar_height=60,
            leading=self.drawer_button,
            automatically_imply_leading=False,
            title=self.title_container,
            force_material_transparency=True,
            center_title=False,
            actions=[
                self.profile_button
            ]
        )

        # Floating action buttons for detection
        self.action_buttons = ft.Column(
            [
                # ft.ElevatedButton(
                #     icon=ft.Icons.CAMERA_ALT,
                #     text="Live Detection",
                #     style=ft.ButtonStyle(
                #         shape=ft.StadiumBorder(),
                #         padding=ft.padding.all(15),
                #     ),
                #     on_click=lambda e: print("Camera Detection")
                # ),
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
            mini=True,
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
                controls=self.home_instance.build(),
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

    def on_drawer_change(self, e):
        """Handle drawer navigation changes"""
        selected = self.drawer.selected_index

        # Navigate to selected page
        if selected in self.navigation_map:
            title, builder = self.navigation_map[selected]
            self.current_view_instance = builder # Update current view instance
            self.current_title = title

            self.show_content_page(title, lambda _: builder.build())
            
            # Lazy load if applicable
            if hasattr(self.current_view_instance, "lazy_load"):
                self.page.run_task(self.current_view_instance.lazy_load)

        # Close drawer after selection
        self.drawer.open = False
        self.page.update()

    # Search Toggle Logic 
    def toggle_search(self, e):
        """Toggle search bar in AppBar for some pages."""
        self.search_active = not self.search_active
        self.title_container.controls.clear()
        search_val = self.search_bar.value

        if self.search_active:
            # Show search bar
            self.title_container.controls.append(self.search_bar)
            self.search_button.icon = ft.Icons.CLOSE
        else:
            if search_val:
                # Clear any active search filters
                self.current_view_instance.filter_content("")

            # Restore normal title
            self.title_container.controls.append(self.normal_title)
            self.search_button.icon = ft.Icons.SEARCH
            self.search_bar.value = None

        self.page.update()

    # Called whenever user types text in SearchBar
    def on_search(self, query: str):
        """Filter content based on search query."""
        time.sleep(1)  # Small delay to allow typing to stabilize
        self.current_view_instance.filter_content(query)

    # Navigation helper
    def show_content_page(self, title: str, content_builder: callable):
        self.normal_title.value = title

        # Reset title container
        self.title_container.controls.clear()
        self.title_container.controls.append(self.normal_title)
        self.search_active = False

        # Reset AppBar actions
        self.appbar.actions = []

        searchable_views = ["Groups", "Gallery"]

        # Insert search only for Gallery
        if title in searchable_views:
            self.appbar.actions.append(self.search_button)

            # If coming from search, restore search bar
            self.title_container.controls.clear()
            self.title_container.controls.append(self.normal_title)
            self.search_button.icon = ft.Icons.SEARCH

        self.appbar.actions.append(self.profile_button)

        # Set page content
        self.body_content.content.controls = content_builder(self.page)
        self.page.update()

    def open_profile(self, e):
        """Enter profile mode with editable fields and avatar upload"""

        # Save current appbar state
        self.temp_appbar_state = {
            "leading": self.appbar.leading,
            "title": self.appbar.title,
            "actions": self.appbar.actions.copy(),
            "force_material_transparency": self.appbar.force_material_transparency,
        }

        # Update appbar for profile
        self.appbar.leading = None  # remove drawer icon
        self.appbar.title = ft.Container(
            ft.Text("Your Profile", size=18, weight="bold"),
            padding=ft.padding.only(left=10)
        )
        self.appbar.actions = [self.close_profile_button]
        self.appbar.force_material_transparency = True

        # Hide FAB
        self.detect_button.visible = False
        self.action_buttons.visible = False

        # Update body
        self.body_content.content.controls = self.profile_instance.build()

        self.page.update()

    def close_profile(self, e):
        """Exit profile mode"""
        if hasattr(self, "temp_appbar_state"):
            self.appbar.leading = self.temp_appbar_state["leading"]
            self.appbar.title = self.temp_appbar_state["title"]
            self.appbar.actions = self.temp_appbar_state["actions"]
            self.appbar.force_material_transparency = self.temp_appbar_state["force_material_transparency"]

        # Restore FAB
        self.detect_button.visible = True

        # Restore previous content
        self.body_content.content.controls = self.current_view_instance.build()
        if hasattr(self.current_view_instance, "lazy_load"):
            self.page.run_task(self.current_view_instance.lazy_load)

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

    def show_detect(self, e):
        """Handle New Detection action"""
        ...