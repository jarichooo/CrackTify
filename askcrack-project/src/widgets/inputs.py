import flet as ft

class AppTextField(ft.TextField):
    def __init__(
        self,
        label: str | None = None,
        hint_text: str | None = None,
        prefix_icon: ft.Icons | None = None,
        width: float | None = None,
        border_color: ft.Colors | None = ft.Colors.BLUE_ACCENT_100,
        border_radius: ft.BorderRadius | None = ft.border_radius.all(10),
        **kwargs
    ) -> None:
        super().__init__(
            label=label,
            hint_text=hint_text,
            prefix_icon=prefix_icon,
            width=width,
            border_color=border_color,
            border_radius=border_radius,
            **kwargs
        )
