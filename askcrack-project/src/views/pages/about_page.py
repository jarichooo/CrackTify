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
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(height=20, opacity=0),
            ft.Text("App Version: 1.0.0", theme_style="bodySmall"),
            ft.Divider(height=20, opacity=0),
        ]

        # Academic Fulfillment Section
        academic_fulfillment = ft.Column(
            controls=[
                ft.Text(
                    "Project Fulfillment", 
                    theme_style="titleMedium"
                ),
                ft.Text(
                    "This project is developed in partial fulfillment of the requirements for the following courses:",
                    theme_style="bodyMedium",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=5, opacity=0),
                ft.Column(
                    controls=[
                        ft.Text("🧑‍💻 Application Development and Emerging Technologies", theme_style="bodySmall"),
                        ft.Text("🔐 Information Assurance and Security", theme_style="bodySmall"),
                        ft.Text("🧑‍💻 Software Engineering 1", theme_style="bodySmall"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    spacing=2
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # Repository Link Section
        repository_section = ft.Column(
            controls=[
                ft.Divider(height=20, opacity=0),
                ft.Text("CrackTify", theme_style="titleMedium"),
                ft.TextButton(
                    text="View on GitHub 🔗",
                    icon=ft.Icons.LINK,
                    on_click=lambda e: self.page.launch_url("https://github.com/jarichooo/CrackTify")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # Developers Section
        developers = ft.Column(
            controls=[
                ft.Divider(height=20, opacity=0),
                ft.Text("Developers", theme_style="titleMedium"),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            text="John Louie Bagaporo",
                            on_click=lambda e: self.page.launch_url("https://github.com/johnlouie2004")
                        ),
                        ft.TextButton(
                            text="Joshua Jericho Barja",
                            on_click=lambda e: self.page.launch_url("https://github.com/jarichooo")
                        ),
                        ft.TextButton(
                            text="Ven Lavapie",
                            on_click=lambda e: self.page.launch_url("https://github.com/ven-62")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # Contact Section
        contact_section = ft.Column(
            controls=[
                ft.Divider(height=20, opacity=0),
                ft.Text("Contact / Support", theme_style="titleMedium"),
                ft.Text("Email: cracktify.noreply@gmail.com", theme_style="bodySmall"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # Combine all sections
        container = ft.Column(
            # In Order: App Info, Academic, Repository, Developers, Contact
            controls=self.content + [academic_fulfillment, repository_section, developers, contact_section],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        return [container]