import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Welcome to the Home Page!", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("This is the main landing page of the AskCrack project.", size=16),
    ]
