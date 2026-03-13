import asyncio
import datetime
import time
import flet as ft

from .template import TemplatePage
from services.crack_service import fetch_cracks_service
from utils.file_utils import build_thumb
from utils.page_utils import show_full
from utils.time_utils import convert_to_utc8


class SearchPage(TemplatePage):

    async def get_cracks(self):
        res = await fetch_cracks_service(self.user.get("id"))

        if not res.get("success"):
            self.search_body.content = ft.Text(
                "Failed to load files.",
                size=20,
                weight="bold",
                color=ft.Colors.RED,
            )
            self.page.update()
            return []

        return res.get("cracks", [])

    async def load_cracks(self):
        self.crack_files = await self.get_cracks()
        self.page.update()

    def __init__(self, page: ft.Page, user: dict = None):
        super().__init__(page)

        self.user = user
        self.crack_files = []

        # schedule async task
        self.page.run_task(self.load_cracks)

    def build(self) -> ft.View:
        """Builds the search page view with app bar and body content."""
        self.search_bar = ft.SearchBar(
            bar_hint_text="Search file name...",
            bar_shadow_color=ft.Colors.TRANSPARENT,
            bar_overlay_color=ft.Colors.TRANSPARENT,
            bar_elevation=0,
            bar_bgcolor=ft.Colors.TRANSPARENT,
            bar_padding=ft.Padding(0, 0, 0, 0),
            bar_trailing=ft.IconButton(
                icon=ft.Icons.CLOSE,
                visible=False,  # Initially hidden, will be shown when user types
                on_click=self.delete_search_bar,
            ),
            view_side=ft.BorderSide(style=ft.BorderStyle.NONE),  # Remove border
            autofocus=True,
            on_change=self.on_search_change,
            on_submit=self.on_search_submit,
        )

        self.app_bar = ft.Column(
            controls=[
                ft.AppBar(
                    title=self.search_bar,
                    center_title=True,
                ),
                ft.Divider(
                    height=0.3,
                    color=ft.Colors.with_opacity(
                        opacity=0.5, color=ft.Colors.INVERSE_SURFACE
                    ),
                ),
            ],
            spacing=0,  # remove spacing between AppBar and Divider
        )

        self.search_result = ft.ListView(expand=True, spacing=10)

        self.search_body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=ft.Padding(20, -20, 20, 0),
            content=self.search_result,
        )

        return self.layout(
            route="/search",
            spacing=0,
            controls=[self.app_bar, self.search_body],
        )

    def on_search_change(self, e):
        """Checks if there is text in the search bar and shows/hides the close button accordingly."""
        query = self.search_bar.value
        self.search_body.content = ft.ProgressRing()  # Show loading indicator while filtering
        self.page.update()
        
        if query:
            self.search_bar.bar_trailing.visible = True
            # perform search and display results as user types
            _ = self.filter_content(query)

        else:
            self.search_bar.bar_trailing.visible = False
            self.search_result.controls.clear()
        self.search_bar.update()

    def delete_search_bar(self, e):
        """Clears the search bar and hides the close button."""
        self.search_bar.value = ""
        self.search_result.controls.clear()
        self.search_bar.bar_trailing.visible = False
        self.search_bar.update()

    def on_search_submit(self, e):
        """Handles the search submission event."""
        query = self.search_bar.value
        _ = self.filter_content(query)  # Filter content based on search query

    def filter_content(self, keyword: str):
        """Filter images by keyword using cached files, without build_tile method."""
        # Filter files based on keyword (case-insensitive)
        filtered_files = [
            f
            for f in self.crack_files
            if keyword.lower() in f.get("filename", "").lower()
        ]

        # Clear grid
        self.search_result.controls.clear()
        self.search_body.content = None

        if not filtered_files or not keyword:
            no_result = ft.Container(
                alignment=ft.Alignment.CENTER,
                expand=True,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        ft.Icon(ft.Icons.SEARCH_OFF, size=100, color=ft.Colors.GREY),
                        ft.Text("No image found.", size=20, color=ft.Colors.GREY),
                    ],
                ),
            )
            self.search_body.content = no_result
            self.page.update()
            return

        self.search_result.controls.append(ft.Text("Results", size=20))

        # If results found, build tiles and show grid
        for crack in filtered_files:
            # Extract relevant info with fallbacks
            filename = crack.get("filename", "Unknown File")
            severity = crack.get("severity", "Unknown Severity")
            probability = crack.get("probability", 0)
            date_str = convert_to_utc8(crack.get("detected_at", ""))

            date = date_str.split("T")[0] if "T" in date_str else date_str
            time = date_str.split("T")[1].split(".")[0] if "T" in date_str else ""

            thumb_image = build_thumb(crack, with_playbtn=False)
            thumb_image.on_click = lambda _, crack_file=crack: show_full(self.page, crack_file)

            bgcolor = (
                ft.Colors.GREEN
                if severity == "Low"
                else (
                    ft.Colors.YELLOW
                    if severity == "Medium"
                    else ft.Colors.RED if severity == "High" else ft.Colors.GREEN
                )
            )

            self.search_result.controls.append(
                ft.ListTile(
                    leading=thumb_image,
                    title=ft.Column(
                        controls=[
                            ft.Text(filename, size=16, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                f"Severity: {severity} ({probability*100:.1f}%)",
                                size=14,
                            ),
                        ],
                        spacing=2,
                    ),
                    subtitle=ft.Text(
                        f"Uploaded on {date} at {time}", size=12, color=ft.Colors.GREY
                    ),
                    is_three_line=True,
                    bgcolor=ft.Colors.with_opacity(0.1, bgcolor),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    on_click=lambda _, crack_file=crack: show_full(
                        self.page, crack_file
                    ),
                )
            )

        self.search_body.content = self.search_result
        self.page.update()
