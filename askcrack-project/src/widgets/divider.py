import flet as ft


def or_divider() -> ft.Row:
    """Creates an 'Or' divider row"""
    return ft.Row(
        controls=[
            ft.Container(content=ft.Divider(), expand=True),
            ft.Text("Or", opacity=0.7),
            ft.Container(content=ft.Divider(), expand=True)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )