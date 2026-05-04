import flet as ft
from .template import TemplatePage
from services.notification_service import get_notifications, mark_notification_as_read, delete_notification
from utils.file_utils import build_thumb
from utils.page_utils import show_full

class NotificationPage(TemplatePage):
    def __init__(self, page: ft.Page, user: dict = None, on_back: callable = None):
        super().__init__(page)
        self.user = user
        self.on_back = on_back
        self.notifications = []

    def build(self) -> ft.View:
        def on_back_click(e):
            self.page.views.pop()
            if self.on_back:
                self.on_back()
            else:
                self.page.go("/")

        self.app_bar = ft.Column(
            controls=[
                ft.AppBar(
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back_click),
                    title=ft.Text("Notifications"),
                )
            ],
            spacing=0,
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

    def _get_card_style(self, is_read: bool) -> tuple:
        """Returns (bgcolor, icon_color, opacity) based on read state."""
        if is_read:
            return ft.Colors.TRANSPARENT, ft.Colors.GREY, 1.0
        return ft.Colors.with_opacity(0.1, ft.Colors.BLUE), ft.Colors.BLUE, 1.0

    def notif_card(self, notification: dict, index: int, file: dict | None) -> ft.Card:
        is_read = notification.get("is_read", False)
        bgcolor, icon_color, opacity = self._get_card_style(is_read)

        return ft.Card(
            data=notification.get("id"),  # ← store id here for lookup
            variant=ft.CardVariant.FILLED,
            bgcolor=bgcolor,
            margin=0,
            content=ft.Container(
                opacity=opacity,
                content=ft.ListTile(
                    on_click=lambda e, n=notification: self.page.run_task(
                        self.view_notification_details, n
                    ),
                    is_three_line=True,
                    leading=ft.Icon(
                        notification.get("icon", ft.Icons.NOTIFICATIONS_OUTLINED),
                        size=32,
                        color=icon_color,
                    ) if not file else build_thumb(file=file, img_size=40,),
                    subtitle=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(notification.get("message", "No Message"), max_lines=3),
                            ft.Text(
                                notification.get("created_at", "Just now"),
                                size=13,
                                color=ft.Colors.GREY,
                            ),
                        ],
                    ),
                    trailing=ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                content="Mark as unread" if is_read else "Mark as read",
                                icon=ft.Icons.MARK_EMAIL_UNREAD_OUTLINED if is_read else ft.Icons.MARK_EMAIL_READ_OUTLINED,
                                on_click=lambda e, i=index: self.page.run_task(
                                    self.toggle_read, i
                                ),
                            ),
                            ft.PopupMenuItem(),  # divider
                            ft.PopupMenuItem(
                                content="Delete",
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e, i=index: self.page.run_task(
                                    self._delete, i
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )

    async def toggle_read(self, index: int):
        """Toggles between read and unread."""
        notif = self.notifications[index]
        new_state = not notif.get("is_read", False)

        result = await mark_notification_as_read(notif["id"], is_read=new_state)
        if result.get("success"):
            self.notifications[index]["is_read"] = new_state
            # rebuild just this card
            self.notifications_list.controls[index] = self.notif_card(
                self.notifications[index], index
            )
            self.notifications_list.update()

    async def _delete(self, index: int):
        """Deletes a notification."""
        notif = self.notifications[index]
        result = await delete_notification(notif["id"])
        if result.get("success"):
            self.notifications.pop(index)
            self.notifications_list.controls.pop(index)
            self.notifications_list.update()

    async def load_notifications(self, user_id: int):
        """Loads notifications from the API on page open."""
        data = await get_notifications(user_id)

        self.notifications = data.get("notifications", [])
        for n, i in enumerate(self.notifications):
            file = None
            if n.get("crack_id"):
                from services.crack_service import fetch_one_crack
                res = await fetch_one_crack(n.get("crack_id"))
                file = res.get("crack", None)
            
            self.notifications_list.controls.append(self.notif_card(n, i, file=file))
        # self.notifications_list.controls = [
        #     self.notif_card(n, i, file=None) for i, n in enumerate(self.notifications)
        # ]
        self.notifications_list.update()

    async def handle_notification(self, data: dict):
        """Handles incoming WebSocket push."""
        if data.get("event") != "send_notification":
            return

        notif = data.get("notification")
        if not notif:
            return
        
        await self.load_notifications(self.user.get("id"))  # Refresh entire list to ensure consistency

    async def view_notification_details(self, notification: dict):
        if notification.get("crack_id"):
            from services.crack_service import fetch_one_crack
            res = await fetch_one_crack(notification.get("crack_id"))
            file = res.get("crack")

            show_full(self.page, file)
            return
        
        await self.toggle_read(
            next(i for i, n in enumerate(self.notifications) if n.get("id") == notification.get("id"))
        )