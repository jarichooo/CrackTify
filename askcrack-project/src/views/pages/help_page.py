import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("Help Page", size=24, weight="bold"),
        ft.Text(
            "Find answers to common questions and get support for using the AskCrack application.", 
            size=16,
        ),
    ]