import flet as ft

class HistorySection:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.View:
        """Builds the history Page layout."""
        
        self.body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            content=ft.Text(
                value="Welcome to the History Page!",
                size=24,
                weight="bold",
                color=ft.Colors.PRIMARY
            )
        )

        return [
            self.body
        ]