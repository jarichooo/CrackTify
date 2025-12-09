import asyncio
from pathlib import Path
from PIL import Image
import flet as ft
from typing import List
import os
from datetime import datetime

from services.crack_service import *

from utils.image_utils import image_to_base64
from widgets.inputs import AppTextField, CustomDropdown

class DetectionHistoryPage:
    IMAGES_FOLDER = Path(__file__).parent.parent.parent.parent / "storage" / "data" / "images" / "detected"

    def __init__(self, page: ft.Page):
        self.page = page
        self.cached_files = None
        self.cached_thumbs = {}
        self.ensure_folder()

    def ensure_folder(self):
        if not self.IMAGES_FOLDER.exists():
            self.IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)

    # MAIN BUILD
    def build(self) -> List[ft.Control]:

        # Clear All button
        self.clear_btn = ft.FilledButton(
            "Clear All History",
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self.clear_all,
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
        )

        # Scrollable list
        self.listview = ft.ListView(
            expand=True,
            spacing=10,
            controls=[]
        )

        # Container wrapper
        self.container = ft.Column([
            self.clear_btn,
            self.listview,
        ], expand=True)

        return [self.container]
    
    async def lazy_load(self):
        """ Lazy load images after a short delay to improve UX. """
        await asyncio.sleep(0.1)
        self.load_history()

    def load_history(self):
        """Load detected images from folder (like ImageGallery does)"""

        # Cache file listing if not already done
        if self.cached_files is None:
            self.cached_files = [
                f for f in self.IMAGES_FOLDER.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
            ]

        # FILTER OUT MISSING FILES (important!)
        self.cached_files = [f for f in self.cached_files if f.exists()]

        # Sort by date descending
        files = sorted(self.cached_files, key=lambda f: f.stat().st_mtime, reverse=True)

        # Clear list
        self.listview.controls.clear()

        if not files:
            # Empty state
            self.listview.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.HISTORY, size=100, color=ft.Colors.GREY),
                            ft.Text("No detection history yet.", size=20, color=ft.Colors.GREY),
                            ft.Text("Start detecting cracks to see your history here.", size=14, color=ft.Colors.GREY_600),
                        ],
                        spacing=10,
                    ),
                )
            )
        else:
            for f in files:
                # Thumbnail caching (like ImageGallery)
                if f not in self.cached_thumbs:
                    self.cached_thumbs[f] = image_to_base64(f, (80, 80))

                thumb = self.cached_thumbs[f]
                
                # Get file info
                file_name = f.name
                file_date = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Determine if it's a crack (based on filename pattern)
                is_crack = "_crack_" in file_name.lower()
                result = "Crack detected" if is_crack else "No crack"
                result_color = ft.Colors.RED_400 if is_crack else ft.Colors.GREEN_400

                # Thumbnail preview
                image_control = ft.Image(
                    src_base64=thumb,
                    width=80,
                    height=80,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8),
                )

                # Action buttons
                action_buttons = [
                    ft.FilledButton(
                        "View Full",
                        icon=ft.Icons.FULLSCREEN,
                        bgcolor=ft.Colors.BLUE_400,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, fp=f: self.show_full_image(fp)
                    ),
                    ft.FilledButton(
                        "Delete",
                        icon=ft.Icons.DELETE,
                        bgcolor=ft.Colors.RED_300,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, fp=f: self.delete_dialog(fp)
                    )
                ]

                # Collapse panel (Expandable)
                panel = ft.ExpansionTile(
                    title=ft.Text(file_name, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"{result} • {file_date}", color=result_color),
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                [
                                    image_control,
                                    ft.Column(
                                        [
                                            ft.Text(f"File: {file_name}", size=14),
                                            ft.Text(f"Result: {result}", size=14, weight=ft.FontWeight.BOLD, color=result_color),
                                            ft.Text(f"Date: {file_date}", size=12, color=ft.Colors.GREY),
                                            ft.Row(action_buttons, spacing=10),
                                        ],
                                        spacing=8,
                                        expand=True,
                                    )
                                ],
                                spacing=15,
                            ),
                            padding=10,
                        )
                    ],
                )

                self.listview.controls.append(panel)

        self.page.update()

    def show_full_image(self, file_path: Path):
        """Show full detected image with crack outlines in overlay"""
        base64_img = image_to_base64(file_path, (1200, 1200))

        full_container = ft.Container(
            width=650,
            height=700,
            bgcolor=ft.Colors.BLACK87,
            content=ft.Column(
                expand=True,
                controls=[
                    # Top row with title and close button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                file_path.name, 
                                size=16, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=ft.Colors.WHITE,
                                on_click=lambda e: (
                                    self.page.overlay.remove(full_container),
                                    self.page.update()
                                )
                            )
                        ]
                    ),
                    # Interactive image with zoom/pan
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

    def delete_dialog(self, file_path: Path):
        """ Show delete confirmation dialog. """
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Image"),
            content=ft.Text(f"Are you sure you want to delete '{file_path.name}'? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Delete", on_click=lambda e: self.delete_image(file_path, dlg)),
            ]
        )

        self.page.open(dlg)
    def delete_image(self, file_path: Path, dlg):
        """ Perform the deletion of the file. """
        
        self.page.close(dlg)
        try:
            if file_path.exists():
                file_path.unlink()
            
            # ✅ Force full refresh (rescan folder)
            self.refresh()
            
        except Exception as e:
            print(f"Error deleting: {e}")

    def clear_all(self, e):
        """ Delete all detected images """
        if not self.cached_files:
            return
            
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear All History"),
            content=ft.Text(f"Are you sure you want to delete all {len(self.cached_files)} detected images? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Delete All", on_click=lambda e: self.do_clear_all(dlg)),
            ]
        )
        self.page.open(dlg)

    def do_clear_all(self, dlg):
        """ Actually delete all files """
        self.page.close(dlg)
        
        if self.cached_files:
            for f in self.cached_files:
                try:
                    f.unlink()
                except Exception as ex:
                    print(f"Error deleting {f}: {ex}")
        
        # Clear cache
        self.cached_files = None
        self.cached_thumbs.clear()
        self.load_history()

    def refresh(self):
        self.cached_files = None
        self.cached_thumbs.clear()
        self.load_history()
