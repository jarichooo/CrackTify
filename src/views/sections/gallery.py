import asyncio
from typing import List

import flet as ft
from services.crack_service import fetch_cracks_service
from utils.file_utils import build_thumb
from utils.page_utils import show_full

from model.user import User


class ImageGallery:
    # (Image size, text size) for each view size
    SIZE_MAP = {
        "Small": (90, 12),
        "Medium": (120, 14),
        "Large": (200, 16),
    }

    def __init__(self, page):
        self.page = page
        self.user = User.to_dict()  # Get user data as a dictionary

        self.current_size = "Medium"
        self.current_sort = "Date Descending"
        self.filter_view = "All"

        self.files: list[dict] = []  # cloud files
        # self.gallery_grid: ft.GridView | None = None
        self.filtered_files: list[dict] = []  # files after applying filter/sort

    def build(self) -> List[ft.Control]:
        """Build the gallery section UI."""
        filter_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Filter By"), ft.Icon(ft.Icons.FILTER_LIST)]),
            items=[
                ft.PopupMenuItem(
                    content="All", on_click=lambda _: self.change_filter("All")
                ),
                ft.PopupMenuItem(
                    content="High", on_click=lambda _: self.change_filter("High")
                ),
                ft.PopupMenuItem(
                    content="Mild", on_click=lambda _: self.change_filter("Mild")
                ),
                ft.PopupMenuItem(
                    content="Low", on_click=lambda _: self.change_filter("Low")
                ),
            ],
        )
        sort_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Sort By"), ft.Icon(ft.Icons.SORT)]),
            items=[
                ft.PopupMenuItem(
                    content="Date Descending",
                    on_click=lambda _: self.change_sort("Date Descending"),
                ),
                ft.PopupMenuItem(
                    content="Date Ascending",
                    on_click=lambda _: self.change_sort("Date Ascending"),
                ),
                ft.PopupMenuItem(
                    content="Name A-Z",
                    on_click=lambda _: self.change_sort("Name A-Z"),
                ),
                ft.PopupMenuItem(
                    content="Name Z-A",
                    on_click=lambda _: self.change_sort("Name Z-A"),
                ),
            ],
        )

        size_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("View Size"), ft.Icon(ft.Icons.VIEW_MODULE)]),
            items=[
                ft.PopupMenuItem(
                    content="Small", on_click=lambda _: self.change_size("Small")
                ),
                ft.PopupMenuItem(
                    content="Medium",
                    on_click=lambda _: self.change_size("Medium"),
                ),
                ft.PopupMenuItem(
                    content="Large", on_click=lambda _: self.change_size("Large")
                ),
            ],
        )

        self.top_bar = ft.Container(
            content=ft.Row(
                controls=[filter_popup, sort_popup, size_popup],
                alignment=ft.MainAxisAlignment.END,
                spacing=20,
            )
        )

        self.gallery_grid = ft.GridView(
            expand=True,
            max_extent=self.SIZE_MAP[self.current_size][0],
            child_aspect_ratio=0.75,  # default aspect ratio for thumbnails
            spacing=10,
            run_spacing=10,
        )

        self.body = ft.Container(expand=True, content=ft.Column())

        return [self.body]

    def refresh(self):
        """Public method to trigger gallery refresh from outside (e.g. after upload)."""
        asyncio.create_task(self.lazy_load())

    async def lazy_load(self):
        """Instant load using cached files, background refresh."""

        self.body.content = (
            ft.ProgressRing()
        )  # Show loading indicator while fetching data
        self.page.update()

        # Show existing files immediately
        if self.files:
            self.update_gallery()

        # Fetch in background
        res = await fetch_cracks_service(self.user.get("id"))

        if not res.get("success"):
            self.body.content = ft.Text(
                "Failed to load gallery.", size=20, weight="bold", color=ft.Colors.RED
            )
            self.page.update()
            return

        new_files = res.get("cracks", [])

        # Compare IDs
        old_files = self.files
        # new_ids = {f["id"] for f in new_files}

        if (
            new_files == old_files
        ) and self.files != []:  # if both is equal but not empty, no changes and new feches is not empty
            return  # nothing changed → no UI update

        # Update only if changed
        self.files = new_files
        self.filtered_files = self.files  # Reset filter to show all new files

        self.update_gallery()

    def change_filter(self, filter_view: str):
        """Change the filter view of the gallery."""
        self.filtered_files = [f for f in self.files if filter_view == "All" or f.get("severity") == filter_view]
        self.update_gallery()

    def change_size(self, size: str):
        """Change the thumbnail size in the gallery."""
        self.current_size = size
        self.gallery_grid.max_extent = self.SIZE_MAP[size][0]

        self.update_gallery()

    def change_sort(self, sort: str):
        """Change the sorting order of the gallery."""
        self.current_sort = sort
        self.update_gallery()

    def update_gallery(self):
        """Update the gallery display based on current files, sort, and size."""

        self.gallery_grid.controls.clear()  # Clear existing thumbnails

        if not self.files:  # If no files to display, display a placeholder message
            self.body.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.BROKEN_IMAGE, size=64, color=ft.Colors.GREY),
                    ft.Text("No files uploaded yet.", size=16, color=ft.Colors.GREY),
                    ft.Text(
                        "Detect some cracks to see gallery.",
                        size=16,
                        color=ft.Colors.GREY,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return
        
        if not self.filtered_files:  # If filter results in no files, show message
            self.body.content = ft.Column(
                controls=[
                    self.top_bar,  # Show top bar even when no results to allow changing filter/sort/size
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.SEARCH_OFF, size=64, color=ft.Colors.GREY),
                                ft.Text("No files match the filter.", size=16, color=ft.Colors.GREY),
                                ft.Text(
                                    "Try changing the filter options.",
                                    size=16,
                                    color=ft.Colors.GREY,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return

        # Sort files based on detected_at timestamp or filename
        files = sorted(
            self.filtered_files,
            key=lambda f: (
                f.get("detected_at", 0)
                if "Date" in self.current_sort
                else f.get("filename", "").lower()
            ),
            reverse=self.current_sort in ("Date Descending", "Name Z-A"),
        )

        # Update the body content with the top bar and gallery grid
        self.body.content = ft.Column(
            controls=[
                self.top_bar,
                self.gallery_grid,
            ],
            expand=True,
        )

        txt_size = self.SIZE_MAP[self.current_size][1]

        for f in files:
            # Build and add thumbnail for each file
            thumbnail = build_thumb(f, self.SIZE_MAP[self.current_size][0])
            thumbnail.on_click = lambda _, file=f: show_full(self.page, file, refresh_function=self.refresh)  # Pass refresh function to full view
            self.gallery_grid.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            thumbnail,
                            ft.Text(
                                f.get("filename", "Unknown"),
                                size=txt_size,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        self.page.update()
