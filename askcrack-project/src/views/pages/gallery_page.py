from pathlib import Path
from PIL import Image
import flet as ft
from typing import List

from utils.image_utils import image_to_base64

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
        self.gallery_grid: ft.GridView | None = None

        self.ensure_folder()

    # Utilities
    def ensure_folder(self):
        if not self.IMAGES_FOLDER.exists():
            self.IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)

    # Build UI
    def build(self) -> List[ft.Control]:
        """ Build the gallery page UI. """
        sort_dropdown = ft.Dropdown(
            scale=0.9,
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

        size_dropdown = ft.Dropdown(
            scale=0.9,
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
    

        self.load_images()
        return [self.page_container]

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
        """ Load images from the folder and display them in the grid. """
        files = [
            f for f in self.IMAGES_FOLDER.iterdir()
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
        ]

        # Sorting logic
        match self.current_sort:
            case "Date Descending":
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            case "Date Ascending":
                files.sort(key=lambda x: x.stat().st_mtime)
            case "Name A-Z":
                files.sort(key=lambda x: x.name.lower())
            case "Name Z-A":
                files.sort(key=lambda x: x.name.lower(), reverse=True)

        self.gallery_grid.controls.clear()

        if not files:
            self.gallery_grid.controls.append(ft.Text("No images found."))
        else:
            for f in files:
                self.gallery_grid.controls.append(self.build_tile(f))

        self.page.update()

    # Image Tile
    def build_tile(self, file_path: Path):
        """ Build a tile for the image grid. """
        thumb = image_to_base64(file_path, (140, 140))

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

    def filter_images(self, keyword: str):
        """ Filter images by keyword in filename. """
        files = [
            f for f in self.IMAGES_FOLDER.iterdir()
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"} and keyword.lower() in f.name.lower()
        ]
        self.gallery_grid.controls.clear()

        if not files:
            self.gallery_grid.controls.append(ft.Text("No images found."))
        else:
            for f in files:
                self.gallery_grid.controls.append(self.build_tile(f))

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

    def delete_image(self, file_path: Path, dlg, sheet):
        """ Perform the deletion of the file. """
        self.page.close(sheet)
        self.page.close(dlg)
        try:
            file_path.unlink()
            self.load_images()
        except Exception as e:
            print(e)

    def rename_dialog(self, file_path: Path, sheet):
        """ Show rename dialog. """
        self.page.close(sheet)

        self.rename_field = ft.TextField(label="Filename", value=file_path.stem)


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
        new_name = self.rename_field.value

        if not new_name.strip():
            self.rename_field.error_text = "Filename cannot be empty."
            self.rename_field.update()
            return

        new_file = file_path.parent / (new_name + file_path.suffix)

        try:
            file_path.rename(new_file)
            self.page.close(dlg)
            self.load_images()
        except Exception as e:
            print(e)
