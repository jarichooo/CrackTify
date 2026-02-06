import flet as ft

class TextField(ft.TextField):
    def __init__(
        self,
        value: str | None = None,
        label: str | None = None,
        hint_text: str | None = None,
        prefix_icon: None = None,
        width: float | None = None,
        height: float | None = None,
        border_color: ft.Colors | None = ft.Colors.SURFACE_TINT,
        border_radius: ft.BorderRadius | None = ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        error: str | None = None,
        **kwargs
    ) -> None:
        super().__init__(
            value=value,
            label=label,
            hint_text=hint_text,
            prefix_icon=prefix_icon,
            width=width,
            height=height,
            border_color=border_color,
            border_radius=border_radius,
            error=error,
            on_change=lambda e: self.clear_error(),
            **kwargs
        )

    def clear_error(self):
        """Clears the error text from the TextField."""
        self.error = None
        self.page.update()

class Dropdown(ft.Dropdown):
    def __init__(
        self,
        label: str | None = None,
        options: list[ft.dropdown.Option] | None = None,
        width: float | None = None,
        border_color: ft.Colors | None = ft.Colors.SURFACE_TINT,
        border_radius: ft.BorderRadius | None = ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        **kwargs
    ) -> None:
        super().__init__(
            label=label,
            options=options,
            width=width,
            border_color=border_color,
            border_radius=border_radius,
            **kwargs
        )
