import flet as ft
from typing import List

class AboutPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content: List[ft.Control] = []

    def build(self) -> List[ft.Column]:

        # App Info
        self.content = [
            ft.Text("About Us", theme_style="headlineMedium"),
            ft.Divider(height=20, opacity=0),
            ft.Text(
                "This application is designed to help users find answers to their questions, mainly cracks on walls related questions",
                theme_style="bodyMedium",
            ),
            ft.Divider(height=20, opacity=0),
            ft.Text("App Version: 1.0.0", theme_style="bodySmall"),
            ft.Divider(height=20, opacity=0),
        ]

        # Developers Section with GitHub links
        developers = ft.Column(
            controls=[
                ft.Text("Developers", theme_style="titleMedium"),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            text="John Louie Bagaporo",
                            on_click=lambda e: self.page.launch_url("https://github.com/johnlouie2004")
                        ),
                        ft.TextButton(
                            text="Joshua Jericho Barja",
                            on_click=lambda e: self.page.launch_url("https://https://github.com/jarichooo")
                        ),
                        ft.TextButton(
                            text="Ven Lavapie",
                            on_click=lambda e: self.page.launch_url("https://https://github.com/ven-62")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        )

        # Contact Section
        contact_section = ft.Column(
            controls=[
                ft.Text("Contact / Support", theme_style="titleMedium"),
                ft.Text("Email: cracktify.noreply@gmail.com", theme_style="bodySmall"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        )

        container = ft.Column(
            controls=self.content + [developers, contact_section],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        return [container]
