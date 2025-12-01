import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Reports Page", size=24, weight="bold"),
        ft.Text(
            "View and analyze detailed reports on crack detection and system performance.",
            size=16,
        ),
    ]