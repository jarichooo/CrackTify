import flet as ft
from .template import TemplatePage

class NotificationPage(TemplatePage):
    def __init__(self, page: ft.Page, user: dict = None, on_back: callable = None):
        super().__init__(page)
        self.user = user
        self.on_back = on_back

        self.notifications = []  # Placeholder for notifications data, can be populated from an API

    def build(self) -> ft.View:
        """Builds the notifications page view with app bar and body content."""
        def on_back_click(e):
            self.page.views.pop()  # Go back to previous view
            if self.on_back:
                self.on_back()
            else:
                self.page.go("/")

        self.app_bar = ft.Column(
            controls=[
                ft.AppBar(
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=on_back_click,
                    ),
                    title=ft.Text("Notifications"),
                )
            ],
            spacing=0,  # remove spacing between AppBar and Divider
        )

        self.notifications_list = ft.ListView(expand=True, spacing=10)

        self.notifications_body = ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=ft.Padding(20, -20, 20, 0),
            content=self.notifications_list,
        )

        return self.layout(
            route="/notifications",
            spacing=0,
            controls=[self.app_bar, self.notifications_body],
        )
    
    def notif_card(self, notification: dict) -> ft.Card:
        """Creates a card UI element for a single notification."""
        return ft.Card(
            content=ft.Column(
                controls=[
                    ft.Text(notification.get("title", "No Title"), weight=ft.FontWeight.BOLD),
                    ft.Text(notification.get("message", "No Message")),
                    ft.Text(notification.get("timestamp", "No Timestamp"), size=10, color=ft.Colors.GRAY),
                ],
                spacing=5,
            ),
            padding=10,
            margin=5,
        )