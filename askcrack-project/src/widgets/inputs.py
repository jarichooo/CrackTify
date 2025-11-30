import flet as ft

class AppTextField(ft.TextField):
    def __init__(
        self,
        value: str | None = None,
        label: str | None = None,
        hint_text: str | None = None,
        prefix_icon: ft.Icons | None = None,
        width: float | None = None,
        border_color: ft.Colors | None = ft.Colors.BLUE_ACCENT_100,
        border_radius: ft.BorderRadius | None = ft.border_radius.all(10),
        error_text: str | None = None,
        **kwargs
    ) -> None:
        super().__init__(
            value=value,
            label=label,
            hint_text=hint_text,
            prefix_icon=prefix_icon,
            width=width,
            border_color=border_color,
            border_radius=border_radius,
            error_text=error_text,
            **kwargs
        )

    def clear_error(self):
        self.error_text = None
        self.page.update()
