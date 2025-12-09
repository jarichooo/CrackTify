import asyncio
from pathlib import Path
from PIL import Image
import flet as ft
from typing import List
import os
from datetime import datetime
import re

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
        """Load detected images with confidence-based severity coloring"""

        if self.cached_files is None:
            self.cached_files = [
                f for f in self.IMAGES_FOLDER.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
            ]

        self.cached_files = [f for f in self.cached_files if f.exists()]
        files = sorted(self.cached_files, key=lambda f: f.stat().st_mtime, reverse=True)

        self.listview.controls.clear()

        if not files:
            # Empty state (unchanged)
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
                if f not in self.cached_thumbs:
                    self.cached_thumbs[f] = image_to_base64(f, (80, 80))

                thumb = self.cached_thumbs[f]
                file_name = f.name
                file_date = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                # === Extract confidence score from filename ===
                confidence = self.extract_confidence(file_name)
                severity_text, severity_color = self.get_severity_info(confidence)

                # Thumbnail
                image_control = ft.Image(
                    src_base64=thumb,
                    width=80,
                    height=80,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8),
                )

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

                panel = ft.ExpansionTile(
                    title=ft.Text(file_name, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        f"{severity_text} ({confidence*100:.1f}%) • {file_date}",
                        color=severity_color
                    ),
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                [
                                    image_control,
                                    ft.Column(
                                        [
                                            ft.Text(f"File: {file_name}", size=14),
                                            ft.Text(
                                                f"Severity: {severity_text}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=severity_color
                                            ),
                                            ft.Text(
                                                f"Confidence: {confidence*100:.1f}%",
                                                size=14,
                                                color=severity_color
                                            ),
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

    # === Helper Methods (Add these to your class) ===

    def extract_confidence(self, filename: str) -> float:
        """
        Extract confidence score from filename.
        Supported patterns:
            _conf_0.87
            _0.87_
            _92%_
            crack_0.76
        Returns confidence as float (0.0 to 1.0), default 0.0 if not found
        """
        text = filename.lower()

        # Pattern 1: _conf_0.87 or conf_0.92
        match = re.search(r'_conf[_-]?([0-9]*\.?[0-9]+)', text)
        if match:
            return min(float(match.group(1)), 1.0)

        # Pattern 2: contains number like 0.85 or 92%
        match = re.search(r'([0-9]*\.?[0-9]+)%?', text)
        if match:
            val = float(match.group(1))
            if val <= 1.0:
                return val
            elif val <= 100:
                return val / 100.0

        # Fallback: check for old _crack_ pattern → assume high confidence
        if "_crack_" in text:
            return 0.9  # assume high confidence
        return 0.0  # no crack

    def get_severity_info(self, confidence: float):
        """Return (text, color) based on confidence"""
        if confidence < 0.4:
            return "No Crack", ft.Colors.GREEN_600
        elif confidence < 0.8:
            return "Mild Crack", ft.Colors.ORANGE_600
        else:
            return "Severe Crack", ft.Colors.RED_600
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
