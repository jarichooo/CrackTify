import os
import asyncio
from pathlib import Path
from typing import List

import flet as ft


class ImageGallery:
    def __init__(self, page: ft.Page):
        self.page = page
        self.image_folder = Path("path/to/your/image/folder")  # Update this path accordingly

    def build(self) -> List[ft.Control]:
        """Builds the gallery Page layout."""
        self.body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            content=ft.Text(
                value="Welcome to the Gallery Page!",
                size=24,
                weight="bold",
                color=ft.Colors.PRIMARY
            )
        )

        return [self.body]
