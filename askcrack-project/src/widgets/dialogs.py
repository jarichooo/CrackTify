import flet as ft
from typing import List

class ErrorDialog(ft.AlertDialog):
    def __init__(
        self,
        modal: bool | None = True,
        icon: ft.Control | None = ft.Icon(ft.Icons.ERROR, size=30),
        title: ft.Control | None = None,
        content: ft.Control | None = None,
        alignment: ft.Alignment | None = ft.alignment.center,
        actions: List[ft.Control] | None = None,
        actions_alignment: ft.MainAxisAlignment | None = ft.MainAxisAlignment.END,

        **kwargs
    ) -> None:
        super().__init__(
            modal=modal,
            icon=icon,
            title=title,
            content=content,
            alignment=alignment,
            actions=actions,
            actions_alignment=actions_alignment,
            **kwargs
        )
