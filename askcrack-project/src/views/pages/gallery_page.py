import asyncio
from pathlib import Path
from PIL import Image
import flet as ft
from typing import List
import os

from utils.image_utils import image_to_base64
from widgets.inputs import AppTextField, CustomDropdown

class ImageGallery:
    IMAGES_FOLDER = Path(__file__).parent.parent.parent.parent / "storage" / "data" / "images" / "detected"

    SIZE_MAP = {
        "Small": 100,
        "Medium": 150,
        "Large": 300,
    }

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_sort = "Date Descending"
        self.current_size = "Medium"

        self.cached_files = None
        self.cached_thumbs = {}

        self.gallery_grid: ft.GridView | None = None
        self.ensure_folder()

    def what_platform(self):
        is_android = os.path.exists("/system/build.prop")
        return 'Android' if is_android else 'Desktop'
    
        self.user_id = self.page.client_storage.get("user").get("id")

    # Utilities
    def ensure_folder(self):
        if not self.IMAGES_FOLDER.exists():
            self.IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)

    # Build UI
    def build(self) -> List[ft.Control]:
        """ Build the gallery page UI. """
        sort_dropdown = CustomDropdown(
            label="Sort By",
            expand=1,
            value=self.current_sort,
            options=[
                ft.dropdown.Option("Date Descending"),
                ft.dropdown.Option("Date Ascending"),
                ft.dropdown.Option("Name A-Z"),
                ft.dropdown.Option("Name Z-A"),
            ],
            on_change=self.on_sort_change
        )

        size_dropdown = CustomDropdown(
            label="View Size",
            expand=1,
            value=self.current_size,
            options=[
                ft.dropdown.Option("Small"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Large"),
            ],
            on_change=self.on_size_change
        )

        self.gallery_grid = ft.GridView(
            expand=True,
            max_extent=self.SIZE_MAP[self.current_size],
            child_aspect_ratio=1,
            spacing=10,
            run_spacing=10,
        )

        self.top_row = ft.Container(
            padding=ft.padding.only(top=20),
            content=ft.Row(
                [sort_dropdown, size_dropdown],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        )

        self.page_container = ft.Column(
            expand=True,
            controls=[
                self.top_row,
                self.gallery_grid
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
        return [self.page_container]
    
    async def lazy_load(self):
        """ Lazy load images after a short delay to improve UX. """
        await asyncio.sleep(0.1)
        self.load_images()

    # Sorting & Size Events
    def on_sort_change(self, e):
        """ Change the sorting of the images. """
        self.current_sort = e.control.value
        self.load_images()

    def on_size_change(self, e):
        """ Change the size of the image tiles. """
        self.current_size = e.control.value
        self.gallery_grid.max_extent = self.SIZE_MAP[self.current_size]
        self.gallery_grid.update()

    # Load & Display Images
    def load_images(self):
        """Load image file list and thumbnails (cached)."""

        # Cache file listing
        if self.cached_files is None:
            self.cached_files = [
                f for f in self.IMAGES_FOLDER.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
            ]
        
        # ✅ Filter out files that no longer exist (in case they were deleted)
        self.cached_files = [f for f in self.cached_files if f.exists()]

        # Apply sorting
        files = sorted(self.cached_files, key=self.sort_key(), reverse=self.sort_reverse())

        # Clear grid
        self.gallery_grid.controls.clear()

        if not files:
            self.gallery_grid.controls.append(ft.Text("No images found."))
        else:
            for f in files:
                # Thumbnail caching (FAST)
                if f not in self.cached_thumbs:
                    self.cached_thumbs[f] = image_to_base64(f, (140, 140))

                thumb = self.cached_thumbs[f]
                self.gallery_grid.controls.append(self.build_tile_thumb(f, thumb))

        self.page.update()

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
    
    def build_tile_thumb(self, file_path: Path, thumb: str):
        """ Build a tile for the image grid using cached thumbnail. """
        return ft.Container(
            border_radius=10,
            padding=10,
            on_click=lambda e: self.show_full(file_path),
            on_long_press=lambda e: self.show_actions(file_path),
            content=ft.Column([
                ft.Image(src_base64=thumb, fit=ft.ImageFit.CONTAIN),
                ft.Text(file_path.name, size=12, overflow=ft.TextOverflow.ELLIPSIS),
            ])
        )

    # Full Image
    def show_full(self, file_path: Path):
        """ Show full image in overlay with zoom and pan. """
        base64_img = image_to_base64(file_path, (1200, 1200))

        full_container = ft.Container(
            width=650,
            height=700,
            bgcolor=ft.Colors.BLACK87,
            content=ft.Column(
                expand=True,
                controls=[
                    # Top row with close button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda e: (
                                    self.page.overlay.remove(full_container),
                                    self.page.update()
                                )
                            )
                        ]
                    ),
                    # Interactive image
                    ft.InteractiveViewer(
                        ft.Image(
                            src_base64=base64_img,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Icon(ft.Icons.BROKEN_IMAGE, size=50, color=ft.Colors.RED)
                        ),
                        expand=True,
                        scale_enabled=True,
                        pan_enabled=True,
                    )
                ]
            )
        )

        # Add to overlay
        self.page.overlay.append(full_container)
        self.page.update()

    def filter_content(self, keyword: str):
        """Filter images by keyword using cached files, without build_tile method."""

        # Ensure cached files
        if not hasattr(self, "cached_files"):
            self.cached_files = [
                f for f in self.IMAGES_FOLDER.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
            ]

        # Filter
        filtered_files = [f for f in self.cached_files if keyword.lower() in f.name.lower()]

        # Clear grid
        self.gallery_grid.controls.clear()

        # Remove existing "no result" container
        self.page_container.controls = [
            c for c in self.page_container.controls
            if getattr(c, "is_no_result", False) != True
        ]

        if filtered_files:
            # Ensure grid is visible
            if self.gallery_grid not in self.page_container.controls:
                self.page_container.controls.append(self.gallery_grid)

            # Build tiles inline
            for f in filtered_files:
                thumb = image_to_base64(f, (140, 140))
                tile = ft.Container(
                    border_radius=10,
                    padding=10,
                    on_click=lambda e, fp=f: self.show_full(fp),
                    on_long_press=lambda e, fp=f: self.show_actions(fp),
                    content=ft.Column([
                        ft.Image(src_base64=thumb, fit=ft.ImageFit.CONTAIN),
                        ft.Text(f.name, size=12, overflow=ft.TextOverflow.ELLIPSIS),
                    ])
                )
                self.gallery_grid.controls.append(tile)
        else:
            # Remove grid and show "no results"
            if self.gallery_grid in self.page_container.controls:
                self.page_container.controls.remove(self.gallery_grid)

            no_result = ft.Container(
                alignment=ft.alignment.center,
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
            no_result.is_no_result = True
            self.page_container.controls.append(no_result)

        self.page.update()

    # Actions (Rename / Delete)
    def show_actions(self, file_path: Path):
        """ Show bottom sheet with actions for the image. """
        sheet = ft.BottomSheet(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Select Action", size=20, weight=ft.FontWeight.BOLD),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.EDIT),
                        title=ft.Text("Rename"),
                        on_click=lambda e: self.rename_dialog(file_path, sheet)
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED),
                        title=ft.Text("Delete"),
                        on_click=lambda e: self.delete_dialog(file_path, sheet)
                    ),
                ])
            )
        )
        self.page.open(sheet)

    def delete_dialog(self, file_path: Path, sheet):
        """ Show delete confirmation dialog. """
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Image"),
            content=ft.Text(f"Are you sure you want to delete '{file_path.name}'? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Delete", on_click=lambda e: self.delete_image(file_path, dlg, sheet)),
            ]
        )

        self.page.open(dlg)

    def delete_image(self, file_path: Path, dlg, sheet=None, history_page=None):
        self.page.close(sheet)
        self.page.close(dlg)
        try:
            file_path.unlink()
            self.cached_files = None
            self.cached_thumbs.pop(file_path, None)
            self.load_images()
            
            # Refresh history page if provided
            if history_page:
                history_page.refresh()
                
        except Exception as e:
            print(e)


    def rename_dialog(self, file_path: Path, sheet):
        """ Show rename dialog. """
        self.page.close(sheet)

        self.rename_field = AppTextField(
            label="New Filename",
            value=file_path.stem,
        )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Rename Image"),
            content=ft.Container(content=self.rename_field, width=320),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Rename", on_click=lambda e: self.do_rename(file_path, dlg)),
            ]
        )

        self.page.open(dlg)

    def do_rename(self, file_path: Path, dlg):
        """ Perform the renaming of the file. """
        new_name = self.rename_field.value.strip()
        if not new_name:
            self.rename_field.error_text = "Filename cannot be empty."
            self.rename_field.update()
            return

        new_file = file_path.parent / (new_name + file_path.suffix)
        try:
            file_path.rename(new_file)
            # Update cache: remove old file, add new
            if self.cached_files:
                try:
                    idx = self.cached_files.index(file_path)
                    self.cached_files[idx] = new_file
                except ValueError:
                    # file not in cache yet
                    self.cached_files.append(new_file)
            self.cached_thumbs.pop(file_path, None)
            self.load_images()
            self.page.close(dlg)
        except Exception as e:
            print(e)
    
    def refresh(self):
        """Refresh detection history - clear cache and reload"""
        self.cached_files = None
        self.cached_thumbs.clear()
        self.load_images()
