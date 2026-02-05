import os
import asyncio
from dataclasses import dataclass, field

import flet as ft
import flet_video as ftv

from .template import TemplatePage
from .more_page import MorePage

from views.sections.home import HomeSection
from views.sections.gallery import ImageGallery
from views.sections.history import HistorySection

from utils.themes import toggle_theme

@dataclass
class State:
    file_path: ft.FilePicker | None = None
    picked_file: list[ft.FilePickerFile] = field(default_factory=list)


class MainPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        # Initialize state
        self.state = State()

        # Initialize page sections instances for navigation
        self.home_page = HomeSection(page)
        self.gallery_page = ImageGallery(page)
        self.history_page = HistorySection(page)

        self.active_section = self.home_page
      
        self.file_picker = ft.FilePicker()

        # Progress bars for uploads
        self.prog_bar: dict[str, ft.ProgressRing] = {}

    def build(self) -> ft.View:
        self.app_bar = ft.AppBar(
            title=ft.Text("Cracktify"),
            automatically_imply_leading=False,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE if self.is_light else ft.Icons.DARK_MODE,
                    tooltip="Toggle Theme",
                    on_click=lambda _: toggle_theme(self.page, self.app_bar.actions[0]),
                )
            ]
        )
        
        self.upload_progress = ft.Container(
            content=ft.ProgressBar(value=0),
            visible=False,
            height=4,
            expand=True,
        )


        self.body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=self.active_section.build()[0]
        )

        # Floating button to trigger picker
        self.pick_file_button = ft.FloatingActionButton(
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Select File",
            on_click=self.handle_files_pick,
        )

        self.nav_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self.on_nav_change,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.PHOTO_LIBRARY, label="Gallery"),
                ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="History"),
                ft.NavigationBarDestination(icon=ft.Icons.MORE_HORIZ, label="More"),
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
            )
        )
    
    def on_upload_progress(self, e: ft.FilePickerUploadEvent):
        self.upload_progress.visible = True
        self.upload_progress.content.value = e.progress
        self.upload_progress.update()

        if e.progress == 1:
            self.upload_progress.visible = False
            self.preview_content.update()

    async def handle_files_pick(self, e: ft.Event[ft.Button]):
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
        from .preview_page import PreviewPage
        preview_page = PreviewPage(self.page, file, self.state)
        self.page.views.append(preview_page.build())


    def on_nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.active_section = self.home_page
            self.pick_file_button.visible = True
            self.app_bar.title = ft.Text("Cracktify")
            self.app_bar.automatically_imply_leading = False
        elif index == 1:
            self.active_section = self.gallery_page
            self.pick_file_button.visible = False
            self.app_bar.title = ft.Text("Gallery")
            self.app_bar.automatically_imply_leading = False
        elif index == 2:
            self.active_section = self.history_page
            self.pick_file_button.visible = False
            self.app_bar.title = ft.Text("History")
            self.app_bar.automatically_imply_leading = False
        elif index == 3:
            self.page.views.append(MorePage(self.page).build())
            return

        self.app_bar.update()
        self.body.content = self.active_section.build()[0]

        if hasattr(self.active_section, "update_gallery"):
            self.active_section.update_gallery()

        self.body.update()