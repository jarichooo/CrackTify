import asyncio
from dataclasses import dataclass, field
import json
import os

import flet as ft
import flet_video as ftv

from views.verify_engineer import VerifyEngineerPage

from .template import TemplatePage
from .more_page import MorePage

from views.sections.home import HomeSection
from views.sections.gallery import ImageGallery
from views.sections.history import HistorySection
from views.notification_page import NotificationPage

from utils.themes import toggle_theme

from model.user import User


@dataclass
class State:
    file_path: ft.FilePicker | None = None
    picked_file: list[ft.FilePickerFile] = field(default_factory=list)


class MainPage(TemplatePage, User):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        # Initialize state
        self.state = State()
        self.user: dict = User.to_dict()  # Initialize user data as an empty dictionary
        self.ver_counter = 0  # Counter to track how many times the verification page has been shown in the session

        # Initialize page sections instances for navigation
        self.home_page = HomeSection(page)
        self.gallery_page = ImageGallery(page)
        self.history_page = HistorySection(page)
        self.notification_page = NotificationPage(
            page, on_back=self.refresh_current_section
        )

        self.page.run_task(
            self.home_page.rotate_header_loop
        )  # Start header rotation loop for home page

        self.active_section = (
            self.home_page
        )  # Start with home page as the active section

        self.file_picker = (
            ft.FilePicker()
        )  # File picker instance for handling file selection

        self.prev_index = (
            0  # To track previous navigation index for any specific logic if needed
        )

    def build(self) -> ft.View:
        """Builds the main page view with app bar, navigation, and body content."""
        try:
            # App bar with title and actions
            self.search_icon = ft.IconButton(
                icon=ft.Icons.SEARCH,
                tooltip="Search",
                on_click=lambda _: self.open_search_page(),
            )

            self.notification_icon = ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS,
                tooltip="Notifications",
                on_click=lambda _: self.open_notifications_page(),
            )

            self.appbar_upload_button = ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Select File",
                visible=False,  # Initially hidden, only show on Gallery page
                on_click=self.handle_files_pick,
            )
            self.toggle_theme_button = ft.IconButton(
                icon=(
                    ft.Icons.LIGHT_MODE
                    if self.page.theme_mode == ft.ThemeMode.LIGHT
                    else ft.Icons.DARK_MODE
                ),
                tooltip="Toggle Theme",
                on_click=lambda _: asyncio.create_task(
                    toggle_theme(self.page, self.toggle_theme_button)
                ),
            )
            self.app_bar = ft.AppBar(
                title=ft.Text("Cracktify"),
                automatically_imply_leading=False,
                force_material_transparency=True,
                actions=[
                    self.appbar_upload_button,
                    self.search_icon,
                    self.notification_icon,
                    self.toggle_theme_button,
                ],
            )

            # Upload progress bar container
            self.upload_progress = ft.Container(
                content=ft.ProgressBar(value=0),
                visible=False,
                height=4,
                expand=True,
            )

            self.body = ft.Container(
                padding=20,
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=self.active_section.build()[0],
            )

            # Floating button to trigger picker
            self.pick_file_button = ft.FloatingActionButton(
                content=ft.Text("New Detection"),
                mini=True,
                icon=ft.Icons.ADD,
                tooltip="Select File",
                on_click=self.handle_files_pick,
            )

            self.nav_bar = ft.NavigationBar(
                selected_index=self.prev_index,
                on_change=self.on_nav_change_engineer if self.user.get("is_engineer") else self.on_nav_change,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.Icons.HOME_ROUNDED, label="Home"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.PHOTO_LIBRARY_ROUNDED, label="Gallery"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.HISTORY_ROUNDED, label="History",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.FOLDER_SHARED, label="Report",
                        visible=True if self.user.get("is_engineer") else False # Only show Report tab for verified engineers
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.MORE_HORIZ,
                        label="More",
                    ),
                ],
            )

            return self.layout(
                route="/home",
                appbar=self.app_bar,
                navigation_bar=self.nav_bar,
                floating_action_button=self.pick_file_button,
                controls=ft.Column(
                    expand=True,
                    controls=[self.upload_progress, self.body],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        finally:
            # Trigger initial view manually
            self.page.run_task(self.home_page.lazy_load)
            from .verify_engineer import VerifyEngineerPage

            verify_page = VerifyEngineerPage(self.page)
            self.page.views.append(verify_page.build())

    def open_search_page(self):
        """Navigate to the search page."""
        from views.search_page import SearchPage

        search_page = SearchPage(
            self.page, self.user, on_back=self.refresh_current_section
        )
        self.page.views.append(search_page.build())

    async def open_notifications_page(self):
        """Navigate to the notifications page."""
        
        self.page.views.append(self.notification_page.build())
        await self.notification_page.load_notifications()  # Load notifications after navigating to the page


    def on_upload_progress(self, e: ft.FilePickerUploadEvent):
        """Handle file upload progress events and update the progress bar accordingly."""
        self.upload_progress.visible = True
        self.upload_progress.content.value = e.progress
        self.upload_progress.update()

        if e.progress == 1:
            self.upload_progress.visible = False
            self.preview_content.update()

    async def handle_files_pick(self, e: ft.Event[ft.Button]):
        """Handle file picking and navigate to preview page with the selected file."""
        self.state.file_picker = ft.FilePicker()

        files = await self.state.file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.MEDIA,
            allowed_extensions=["jpg", "png", "mp4", "mov", "webm", "avi", "mkv"],
        )
        if not files:
            return

        file = files[0] 
        self.state.picked_file = [file]

        # Create preview page with file and push it
        from .upload_preview import PreviewPage

        preview_page = PreviewPage(
            self.page,
            file,
            self.state,
            self.user,
            on_close=self.refresh_current_section,  # Pass the refresh function to the preview page to call after upload completes
        )
        self.page.views.append(preview_page.build())

    def refresh_current_section(self):
        """Refresh the current active section (home/gallery/history) after actions like upload or delete."""
        self.active_section.refresh()  # Call the refresh method of the active section

        self.body.update()
    
    
    def on_nav_change_engineer(self, e):
        """Handle navigation bar changes for engineers and update the active section accordingly, including showing the verification page if the user is not verified and tries to access the Report tab."""
        index = e.control.selected_index

        if index == 0:
            self.active_section = self.home_page
            self.app_bar.title = ft.Text("Cracktify")
            self.pick_file_button.visible = True
            self.appbar_upload_button.visible = (
                False  # Hide upload button in app bar for home page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 1:
            self.active_section = self.gallery_page
            self.app_bar.title = ft.Text("Gallery")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = (
                True  # Show upload button in app bar for gallery page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 2:
            self.active_section = self.history_page
            self.app_bar.title = ft.Text("History")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = (
                True  # Show upload button in app bar for history page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 3:
            ... # Report tab - only accessible to verified engineers

        elif index == 4:
            more_page = MorePage(self.page)
            self.page.views.append(more_page.build())
            return

        self.prev_index = index  # Update previous index
        self.app_bar.update()
        self.body.content = self.active_section.build()[0]

        if hasattr(self.active_section, "lazy_load"):
            asyncio.create_task(self.active_section.lazy_load())

        self.body.update()


    def on_nav_change(self, e):
        """Handle navigation bar changes and update the active section accordingly."""
        index = e.control.selected_index

        if index == 0:
            self.active_section = self.home_page
            self.app_bar.title = ft.Text("Cracktify")
            self.pick_file_button.visible = True
            self.appbar_upload_button.visible = (
                False  # Hide upload button in app bar for home page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 1:
            self.active_section = self.gallery_page
            self.app_bar.title = ft.Text("Gallery")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = (
                True  # Show upload button in app bar for gallery page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 2:
            self.active_section = self.history_page
            self.app_bar.title = ft.Text("History")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = (
                True  # Show upload button in app bar for history page
            )
            self.app_bar.automatically_imply_leading = False

        elif index == 3:
            more_page = MorePage(self.page)
            self.page.views.append(more_page.build())
            return

        self.prev_index = index  # Update previous index
        self.app_bar.update()
        self.body.content = self.active_section.build()[0]

        if hasattr(self.active_section, "lazy_load"):
            asyncio.create_task(self.active_section.lazy_load())

        self.body.update()
