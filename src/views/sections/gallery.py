import asyncio
from typing import List

import flet as ft
from services.crack_service import fetch_cracks_service
from utils.file_utils import get_file_type, get_video_thumbnail

class ImageGallery:
    SIZE_MAP = {
        "Small": 80,
        "Medium": 120,
        "Large": 200,
    }

    def __init__(self, page: ft.Page, user: dict):
        self.page = page
        self.user = user

        self.current_size = "Medium"
        self.current_sort = "Date Descending"

        self.files: list[dict] = []  # cloud files
        # self.gallery_grid: ft.GridView | None = None

    def build(self) -> List[ft.Control]:
        """Build the gallery section UI."""
        sort_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Sort By"), ft.Icon(ft.Icons.SORT)]),
            items=[
                ft.PopupMenuItem(content="Date Descending", on_click=lambda _: self.change_sort("Date Descending")),
                ft.PopupMenuItem(content="Date Ascending", on_click=lambda _: self.change_sort("Date Ascending")),
            ],
        )

        size_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("View Size"), ft.Icon(ft.Icons.VIEW_MODULE)]),
            items=[
                ft.PopupMenuItem(content="Small", on_click=lambda _: self.change_size("Small")),
                ft.PopupMenuItem(content="Medium", on_click=lambda _: self.change_size("Medium")),
                ft.PopupMenuItem(content="Large", on_click=lambda _: self.change_size("Large")),
            ],
        )

        self.top_bar = ft.Container(
            content=ft.Row(
                controls=[
                    sort_popup,
                    size_popup
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=20,
            )
        )

        self.gallery_grid = ft.GridView(
            expand=True,
            max_extent=self.SIZE_MAP[self.current_size],
            spacing=10,
            run_spacing=10,
        )

        self.body = ft.Container(
            expand=True,
            content=ft.Column()
        )

        self.page.run_task(self.load_files)

        return [self.body]

    async def load_files(self):
        """Instant load using cached files, background refresh."""

        self.body.content = ft.ProgressRing() # Show loading indicator while fetching data
        self.page.update()

        # Show existing files immediately
        if self.files:
            self.update_gallery()

        # Fetch in background
        res = await fetch_cracks_service(self.user.get("id"))
        if not res.get("success"):
            self.body.content = ft.Text(
                "Failed to load gallery.",
                size=20,
                weight="bold",
                color=ft.Colors.RED
            )
            self.page.update()
            return

        new_files = res.get("cracks", [])

        # Compare IDs
        old_ids = {f["id"] for f in self.files}
        new_ids = {f["id"] for f in new_files}

        if new_ids == old_ids:
            return  # nothing changed → no UI update

        # Update only if changed
        self.files = new_files
        self.update_gallery()

    def change_size(self, size: str):
        """Change the thumbnail size in the gallery."""
        self.current_size = size
        self.gallery_grid.max_extent = self.SIZE_MAP[size]
        self.update_gallery()

    def change_sort(self, sort: str):
        """Change the sorting order of the gallery."""
        self.current_sort = sort
        self.update_gallery()

    def update_gallery(self):
        """Update the gallery display based on current files, sort, and size."""

        self.gallery_grid.controls.clear() # Clear existing thumbnails

        if not self.files: # If no files to display, display a placeholder message
            self.body.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.BROKEN_IMAGE, size=64, color=ft.Colors.GREY),
                    ft.Text("No files uploaded yet. Detect some cracks to see gallery.", size=16, color=ft.Colors.GREY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return

        # Sort files based on detected_at timestamp
        files = sorted(
            self.files,
            key=lambda f: f["detected_at"],
            reverse=self.current_sort == "Date Descending",
        )

        # Update the body content with the top bar and gallery grid
        self.body.content = ft.Column(
            controls=[
                self.top_bar,
                self.gallery_grid,
            ],
            expand=True,
        )

        for f in files:
            # Build and add thumbnail for each file
            self.gallery_grid.controls.append(self.build_thumb(f))

        self.page.update()

    def build_thumb(self, file: dict) -> ft.Control:
        """Build a thumbnail control for a given file."""
        size = self.SIZE_MAP[self.current_size]
        url = file.get("file_url") # Assuming the file dict has a 'file_url' key with the Cloudinary URL
        thumb_url = url # Default thumbnail is the file itself

        is_video = get_file_type(url) == "video"  # Check if the file is a video to generate a thumbnail
        if is_video:
            thumb_url = get_video_thumbnail(url)

        thumbnail_img = ft.Image(
            src=thumb_url,
            width=size,
            height=size,
            fit=ft.BoxFit.COVER,
        )

        content = ft.Stack(
            controls=[
                thumbnail_img,
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL, size=48, color=ft.Colors.WHITE
                    ),
                    alignment=ft.Alignment.CENTER,
                    visible=is_video,
                    bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                ),
            ]
        )

        return ft.Container(
            content=content,
            width=size,
            height=size,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda _: print("Open preview:", url),
        )
