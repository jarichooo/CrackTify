import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Settings Page", size=24, weight="bold"),
        ft.Text(
            "Configure application settings and preferences to customize your experience.",
            size=16,
        ),
    ]