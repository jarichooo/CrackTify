import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Gallery Page", size=24, weight="bold"),
        ft.Text(
            "Explore and manage your collection of images and media related to crack detection.",
            size=16,
        ),
    ]