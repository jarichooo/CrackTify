import os
import asyncio
from pathlib import Path
from typing import List

import flet as ft

from utils.file_utils import image_to_base64, extract_video_thumbnail

class ImageGallery:
    # Directory where uploaded files are stored
    FILES_DIR = Path(__file__).parent.parent.parent / "uploads"
    # Size mapping for thumbnails
    SIZE_MAP = {
        "Small": 50, 
        "Medium": 100, 
        "Large": 200
    }

    def __init__(self, page: ft.Page):
        self.page = page

        # self.FILES_DIR = os.path.join(os.getenv("EXTERNAL_STORAGE"), "Android", "data", "com.mycompany.cracktify", "files", "cracktify")

        self.current_size = "Medium"  # default size
        self.current_sort = "Date Descending"    # default sort
        self.cached_files = None
        self.cached_thumbs = {}

        self.gallery_grid: ft.GridView | None = None

        self.ensure_directory()

    # utility methods
    def ensure_directory(self):
        """Ensures the files directory exists."""
        if not os.path.exists(self.FILES_DIR):
            os.makedirs(self.FILES_DIR, exist_ok=True)

    def build(self) -> List[ft.Control]:
        """Builds the gallery Page layout."""
        # Top bar with sorting and size options
        sort_popup = ft.PopupMenuButton(
            content=ft.Row(
                controls=[ft.Text("Sort By"), ft.Icon(ft.Icons.SORT)]
            ),
            items=[
                ft.PopupMenuItem(content="Date Descending", on_click=lambda _: self.change_sort("Date Descending")),
                ft.PopupMenuItem(content="Date Ascending", on_click=lambda _: self.change_sort("Date Ascending")),
                ft.PopupMenuItem(content="Name A-Z", on_click=lambda _: self.change_sort("Name A-Z")),
                ft.PopupMenuItem(content="Name Z-A", on_click=lambda _: self.change_sort("Name Z-A")),
            ],
        )

        size_popup = ft.PopupMenuButton(
            content=ft.Row(
                controls=[ft.Text("View Size"), ft.Icon(ft.Icons.VIEW_MODULE) ]
            ),
            items=[
                ft.PopupMenuItem(content="Small", on_click=lambda _: self.change_size("Small")),
                ft.PopupMenuItem(content="Medium", on_click=lambda _: self.change_size("Medium")),
                ft.PopupMenuItem(content="Large", on_click=lambda _: self.change_size("Large")),
            ],
        )

        self.top_bar = ft.Container(
            # padding=ft.Padding.only(right=20, left=20),
            content=ft.Row(
                controls=[
                    sort_popup,
                    size_popup
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=20,
            )
        )

        self.refresh_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.CHECK_CIRCLE,
                size=64,
                color=ft.Colors.GREEN,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.with_opacity(1.0, ft.Colors.BLACK),
            visible=False,
            expand=True,
        )


        self.gallery_grid = ft.GridView(
            expand=True,
            max_extent=self.SIZE_MAP[self.current_size],
            child_aspect_ratio=1,
            spacing=10,
            run_spacing=10,
        )

        self.body = ft.GestureDetector(
            on_vertical_drag_update=self.on_vertical_drag,
            expand=True,
            content=ft.Stack(
                # expand=True,
                margin=ft.Margin.all(20),
                controls=[
                    ft.Container(
                        content=ft.Column()
                    ),
                    self.refresh_icon,  # overlay icon
                ]
            )
        )

        return [self.body]
    
    def change_size(self, new_size: str):
        """Changes the thumbnail size and updates the gallery."""
        self.current_size = new_size
        if self.gallery_grid:
            self.gallery_grid.max_extent = self.SIZE_MAP[new_size]
            self.update_gallery()

    def change_sort(self, new_sort: str):
        """Changes the sorting method and updates the gallery."""
        self.current_sort = new_sort
        self.update_gallery()

    def sort_key(self):
        """ Return sorting key function based on current selection. """
        return {
            "Date Descending": lambda f: f.stat().st_mtime,
            "Date Ascending": lambda f: f.stat().st_mtime,
            "Name A-Z": lambda f: f.name.lower(),
            "Name Z-A": lambda f: f.name.lower(),
        }.get(self.current_sort, lambda f: f.stat().st_mtime)
    
    def sort_reverse(self):
        """ Return whether sorting should be in reverse order. """
        return self.current_sort in ("Date Descending", "Name Z-A")

    def get_thumbnail(self, file: Path) -> ft.Control:
        """Generates a thumbnail control for the given file."""
        if file in self.cached_thumbs:
            return self.cached_thumbs[file]
    
        size = self.SIZE_MAP[self.current_size]
        ext = file.suffix.lower()

        # Determine if file is a video
        is_video = ext in [".mp4", ".mov", ".webm", ".avi", ".mkv"]

        # Get thumbnail source
        if is_video and self.page.platform.is_mobile():
            thumb_src = extract_video_thumbnail(file)
        else:
            thumb_src = file

        # Convert to base64 for Flet Image
        imgb_base64 = image_to_base64(thumb_src)
        thumbnail_image = ft.Image(
            src=imgb_base64,
            width=size,
            height=size,
            fit=ft.BoxFit.COVER,
        )

        # Stack image and play icon if video
        content = ft.Stack(
            controls=[
                thumbnail_image,
                # ▶ Play icon overlay for videos
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL,
                        size=48,
                        color=ft.Colors.WHITE,
                    ),
                    alignment=ft.Alignment.CENTER,
                    visible=is_video,
                    bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                ),
            ]
        )

        thumb = ft.Container(
            content=content,
            width=size,
            height=size,
            border_radius=ft.BorderRadius.all(10),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda e, f=file: print(f"Clicked on {f.name}"),
        )

        self.cached_thumbs[file] = thumb
        return thumb

    def update_gallery(self):
        """Updates the gallery display based on current size and sort."""

        # Load files if not cached
        if self.cached_files is None:
            self.cached_files = [
                f for f in self.FILES_DIR.glob("*") if f.is_file()
            ]

        # Update cached files to remove any that no longer exist
        self.cached_files = [
            f for f in self.cached_files if f.exists()
        ]

        # Get sorted
        files = sorted(self.cached_files, key=self.sort_key(), reverse=self.sort_reverse())

        # Clear existing thumbnails
        self.gallery_grid.controls.clear()

        if not files:
            self.body.content.controls = ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PHOTO_LIBRARY, size=100, color=ft.Colors.GREY),
                    ft.Text(value="No files uploaded yet.", size=20, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER)
                ]
            )
            self.page.update()
            return
        
        else:
            self.body.content.controls = ft.Column(
                controls=[
                    self.top_bar,
                    self.gallery_grid
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )
            for f in files:
                thumb = self.get_thumbnail(f)
                self.gallery_grid.controls.append(thumb)

        self.page.update()

    def on_vertical_drag(self, e: ft.DragUpdateEvent):
        if e.primary_delta > 12:
            asyncio.create_task(self.refresh())


    async def refresh(self):
        if getattr(self, "_refreshing", False):
            return

        self._refreshing = True

        self.cached_files = None
        self.cached_thumbs.clear()
        self.update_gallery()

        # Show icon
        self.refresh_icon.visible = True
        self.page.update()

        await asyncio.sleep(1)

        self.refresh_icon.visible = False
        self.page.update()

        self._refreshing = False
