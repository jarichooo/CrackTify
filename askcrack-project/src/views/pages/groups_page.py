import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Groups Page", size=24, weight="bold"),
        ft.Text(
            "Manage and organize groups for crack detection projects and collaborations.",
            size=16,
        ),
    ]