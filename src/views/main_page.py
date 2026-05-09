import asyncio
from dataclasses import dataclass, field
import json
import os

import flet as ft
import flet_video as ftv

from .template import TemplatePage
from .more_page import MorePage

from views.sections.home import HomeSection
from views.sections.gallery import ImageGallery
from views.sections.report import ReportSection
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

        self.state = State()
        self.user: dict = User.to_dict()
        self.ver_counter = 0

        self.home_page = HomeSection(page)
        self.gallery_page = ImageGallery(page)
        self.history_page = HistorySection(page)
        if self.user.get("is_engineer"):
            self.report_page = ReportSection(page)

        self.notification_page = NotificationPage(
            page,
            on_back=self.refresh_current_section,
            on_unread_count=self._update_badge,
        )

        self.page.run_task(self.home_page.rotate_header_loop)

        self.active_section = self.home_page
        self.file_picker = ft.FilePicker()
        self.prev_index = 0

    def build(self) -> ft.View:
        """Builds the main page view with app bar, navigation, and body content."""
        try:
            self.search_icon = ft.IconButton(
                icon=ft.Icons.SEARCH,
                tooltip="Search",
                on_click=lambda _: self.open_search_page(),
            )

            self.notification_icon = ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS,
                tooltip="Notifications",
                on_click=self.open_notifications_page,
                badge=ft.Badge(
                    label="",
                    offset=ft.Offset(-5, 5),
                    bgcolor=ft.Colors.TRANSPARENT,
                    small_size=8,
                    text_color=ft.Colors.TRANSPARENT,
                ),
            )

            self.appbar_upload_button = ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Select File",
                visible=False,
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
                    ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="Home"),
                    ft.NavigationBarDestination(icon=ft.Icons.PHOTO_LIBRARY_ROUNDED, label="Gallery"),
                    ft.NavigationBarDestination(icon=ft.Icons.HISTORY_ROUNDED, label="History"),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.FOLDER_SHARED,
                        label="Report",
                        visible=True if self.user.get("is_engineer") else False,
                    ),
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
                ),
            )
        finally:
            self.page.run_task(self.home_page.lazy_load)
            # Load notifications in background on startup.
            # _is_mounted is False here, so only the badge will update — no list render yet.
            self.page.run_task(self.notification_page.load_notifications, self.user.get("id"))

    def open_search_page(self):
        from views.search_page import SearchPage
        search_page = SearchPage(self.page, self.user, on_back=self.refresh_current_section)
        self.page.views.append(search_page.build())

    async def open_notifications_page(self, e=None):
        """Navigate to the notifications page."""
        # IMPORTANT: build() first so _is_mounted = True, THEN load so the list
        # renders with fresh data. The previous order (load → build) caused the
        # list to always appear empty because _is_mounted was still False during load.
        self.page.views.append(self.notification_page.build())
        self.page.update()
        await self.notification_page.load_notifications(self.user.get("id"))

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

        from .upload_preview import PreviewPage
        preview_page = PreviewPage(
            self.page,
            file,
            self.state,
            self.user,
            on_close=self.refresh_current_section,
        )
        self.page.views.append(preview_page.build())

    def _update_badge(self, unread_count: int):
        """
        Update the notification badge.
        Shows a red badge with count when unread_count > 0.
        Hides it completely when unread_count == 0.
        """
        badge = self.notification_icon.badge
        if unread_count > 0:
            badge.label = str(unread_count)
            badge.bgcolor = ft.Colors.RED
            badge.text_color = ft.Colors.WHITE
            badge.small_size = None     # Use label-sized badge
        else:
            badge.label = ""
            badge.bgcolor = ft.Colors.TRANSPARENT
            badge.text_color = ft.Colors.TRANSPARENT
            badge.small_size = 8        # Collapse back to invisible dot

        try:
            self.notification_icon.update()
        except Exception:
            pass  # Widget not yet mounted on first background load — harmless

    def refresh_current_section(self):
        self.active_section.refresh()
        self.body.update()

    def on_nav_change_engineer(self, e):
        index = e.control.selected_index

        if index == 0:
            self.active_section = self.home_page
            self.app_bar.title = ft.Text("Cracktify")
            self.pick_file_button.visible = True
            self.appbar_upload_button.visible = False
            self.app_bar.automatically_imply_leading = False

        elif index == 1:
            self.active_section = self.gallery_page
            self.app_bar.title = ft.Text("Gallery")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = True
            self.app_bar.automatically_imply_leading = False

        elif index == 2:
            self.active_section = self.history_page
            self.app_bar.title = ft.Text("History")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = True
            self.app_bar.automatically_imply_leading = False

        elif index == 3:
            self.active_section = self.report_page
            self.app_bar.title = ft.Text("Reports")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = True

        elif index == 4:
            more_page = MorePage(self.page)
            self.page.views.append(more_page.build())
            return

        self.prev_index = index
        self.app_bar.update()
        self.body.content = self.active_section.build()[0]

        if hasattr(self.active_section, "lazy_load"):
            asyncio.create_task(self.active_section.lazy_load())

        self.body.update()

    def on_nav_change(self, e):
        index = e.control.selected_index

        if index == 0:
            self.active_section = self.home_page
            self.app_bar.title = ft.Text("Cracktify")
            self.pick_file_button.visible = True
            self.appbar_upload_button.visible = False
            self.app_bar.automatically_imply_leading = False

        elif index == 1:
            self.active_section = self.gallery_page
            self.app_bar.title = ft.Text("Gallery")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = True
            self.app_bar.automatically_imply_leading = False

        elif index == 2:
            self.active_section = self.history_page
            self.app_bar.title = ft.Text("History")
            self.pick_file_button.visible = False
            self.appbar_upload_button.visible = True
            self.app_bar.automatically_imply_leading = False

        elif index == 3:
            more_page = MorePage(self.page)
            self.page.views.append(more_page.build())
            return

        self.prev_index = index
        self.app_bar.update()
        self.body.content = self.active_section.build()[0]

        if hasattr(self.active_section, "lazy_load"):
            asyncio.create_task(self.active_section.lazy_load())

        self.body.update()