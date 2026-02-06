import flet as ft

class AlertDialog(ft.AlertDialog):
    def __init__(
        self, 
        title: str, 
        content: str, 
        actions: list[ft.TextButton] = [],
        **kwargs
    ) -> None:
        actions.append(ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())) if actions == [] else None

        super().__init__(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=actions,
            **kwargs
        )