import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Detection History Page", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("This is the detection history page of the AskCrack project.", size=16),
    ]