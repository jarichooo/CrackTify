import flet as ft

class BackButton(ft.IconButton):
    """A reusable back button widget"""
    def __init__(
        self,
        icon: ft.Icons = ft.Icons.ARROW_BACK,
        tooltip: str = "Back",
        **kwargs
    ) -> None:
        super().__init__(
            icon=icon,
            tooltip=tooltip,
            **kwargs
        )

class PrimaryButton(ft.FilledButton):
    """A reusable primary button widget"""
    def __init__(
        self,
        text: str,
        icon: None = None,
        width: float | None = None,
        height: float = 50,
        style: ft.ButtonStyle | None = ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        **kwargs
    ) -> None:
        super().__init__(
            text,
            icon=icon,
            width=width,
            height=height,
            style=style,
            **kwargs
        )

class SecondaryButton(ft.FilledTonalButton):
    """A reusable secondary button widget"""
    def __init__(
        self,
        text: str,
        icon: None = None,
        width: float | None = None,
        height: float = 50,
        style: ft.ButtonStyle | None = ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
        **kwargs
    ) -> None:
        super().__init__(
            text,
            icon=icon,
            width=width,
            height=height,
            style=style,
            **kwargs
        )

class GoogleButton(ft.FilledTonalButton):
    """A reusable Google sign-in button widget"""
    def __init__(
        self,
        text: str | None = "Sign in with Google",
        icon: ft.Image | None = ft.Image(
            src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg",
            width=24,
            height=24
        ),
        width: float | None = None,
        height: float = 50,
        **kwargs
    ) -> None:
        super().__init__(
            content=ft.Row(
                controls=[
                    icon,
                    ft.Text(text, size=16, weight=ft.FontWeight.NORMAL)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=width,
            height=height,
            **kwargs
        )

class CustomTextButton(ft.GestureDetector):
    def __init__(
        self,
        text: str,
        text_align: ft.TextAlign = ft.TextAlign.CENTER,
        color: ft.Colors = ft.Colors.BLUE,
        weight: str = "bold",
        mouse_cursor: ft.MouseCursor = ft.MouseCursor.CLICK,
        disabled: bool = False,
        **kwargs
    ) -> None:
        super().__init__(
            content=ft.Text(
                text,
                text_align=text_align,
                color=color,
                weight=weight
            ),
            disabled=disabled,
            mouse_cursor=mouse_cursor,
            **kwargs
        )