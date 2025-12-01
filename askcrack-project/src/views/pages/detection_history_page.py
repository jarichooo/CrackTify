import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Admin Dashboard", size=24, weight="bold"),
        ft.Text(
            "Welcome to the Admin Dashboard. Here you can manage users, view system statistics, and configure application settings.",
            size=16,
        ),
    ]