import flet as ft
from typing import List

def build(page) -> List[ft.Control]:
    return [
        ft.Text("About Cracktify", size=24, weight="bold"),
        ft.Text(
            "Cracktify is a cutting-edge application designed to help users detect and analyze cracks in various materials using advanced algorithms and machine learning techniques.",
            size=16,
        ),
        ft.Text(
            "Our mission is to provide accurate and efficient crack detection solutions to enhance safety and maintenance processes across industries.",
            size=16,
        ),
    ]