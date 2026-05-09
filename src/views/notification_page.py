from widgets.buttons import PrimaryButton, SecondaryButton
from .template import TemplatePage
from services.notification_service import (
    get_notifications,
    mark_notification_as_read,
    delete_notification,
)
from utils.file_utils import build_thumb
from utils.page_utils import show_full
import flet as ft
from model.user import User


class NotificationPage(TemplatePage):
    def __init__(
        self, page: ft.Page, on_back: callable = None, on_unread_count: callable = None
    ):
        super().__init__(page)
        self.user = User.to_dict()
        self.on_back = on_back
        self.on_unread_count = on_unread_count
        self.notifications = []
        self.special_notification_ids: dict[int, int] = {}
        self._is_mounted = False

        # NOTE: No asyncio.create_task() here. load_notifications() is the
        # single entry point for fetching — called explicitly from MainPage.build()
        # via page.run_task(), and again inside open_notifications_page() after build().

    #  View builder                                                       #

    def build(self) -> ft.View:
        def on_back_click(e):
            self._is_mounted = False
            self.page.views.pop()
            if self.on_back:
                self.on_back()
            else:
                self.page.go("/")

        self.app_bar = ft.Column(
            controls=[
                ft.AppBar(
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK, on_click=on_back_click
                    ),
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

        # Mark mounted BEFORE populating so _rebuild_list() inside load_notifications
        # (called right after build()) can call .update() correctly.
        self._is_mounted = True

        # Render whatever is already in memory (avoids blank flash if WS pushed
        # notifications before the page was opened).
        self._populate_list()

        return self.layout(
            route="/notifications",
            spacing=0,
            controls=[self.app_bar, self.notifications_body],
        )

    #  Badge                                                              #

    def _emit_badge(self):
        """Compute unread count and fire on_unread_count. Always safe to call."""
        if self.on_unread_count:
            unread = sum(1 for n in self.notifications if not n.get("is_read", False))
            self.on_unread_count(unread)

    #  List rendering                                                     #

    def _populate_list(self):
        """Write cards into notifications_list.controls. Does NOT call .update()."""
        self.notifications_list.controls = [
            self.notif_card(n, i, file=n.get("_file"))
            for i, n in enumerate(self.notifications)
        ]
        if not self.notifications_list.controls:
            self.notifications_list.controls.append(
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding(20),
                    content=ft.Text(
                        "No notifications yet.", size=18, color=ft.Colors.GREY
                    ),
                )
            )

    def _rebuild_list(self):
        """
        Rebuild all cards, update screen (if mounted), and fire badge update.
        Safe to call at any time — WS handler, load, delete, toggle, etc.
        """
        self._emit_badge()  # Always update badge

        if not self._is_mounted:
            return  # Page not open — skip UI update

        self._populate_list()
        self.notifications_list.update()

    #  Card builder                                                       #

    def _get_card_style(self, is_read: bool) -> tuple:
        if is_read:
            return ft.Colors.TRANSPARENT, ft.Colors.GREY, 1.0
        return ft.Colors.with_opacity(0.1, ft.Colors.BLUE), ft.Colors.BLUE, 1.0

    def notif_card(
        self, notification: dict, index: int, file: dict | None = None
    ) -> ft.Card:
        is_read = notification.get("is_read", False)
        bgcolor, icon_color, opacity = self._get_card_style(is_read)
        notif_id = notification.get("id")
        actions = None

        if notif_id in self.special_notification_ids:
            actions = ft.Container(
                ft.Row(
                    controls=[
                        PrimaryButton(
                            "Accept",
                            color=ft.Colors.GREEN,
                            on_click=lambda e, n=notification: self.page.run_task(
                                self.accept_invitation, n
                            ),
                        ),
                        SecondaryButton(
                            "Ignore",
                            color=ft.Colors.GREY,
                            on_click=lambda e, i=index: self.page.run_task(
                                self.toggle_read, i
                            ),
                        ),
                    ],
                    spacing=4,
                )
            )

        def on_tile_click(e, n=notification):
            if n.get("crack_id"):
                self.page.run_task(self.view_crack_details, n)
            else:
                self.page.run_task(self.toggle_read, index)

        return ft.Card(
            data=notif_id,
            variant=ft.CardVariant.FILLED,
            bgcolor=bgcolor,
            margin=0,
            content=ft.Container(
                opacity=opacity,
                content=ft.ListTile(
                    on_click=on_tile_click,
                    is_three_line=True,
                    leading=(
                        build_thumb(file=file, img_size=40)
                        if file
                        else ft.Icon(
                            notification.get("icon", ft.Icons.NOTIFICATIONS_OUTLINED),
                            size=32,
                            color=icon_color,
                        )
                    ),
                    subtitle=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                notification.get("message", "No Message"), max_lines=3
                            ),
                            ft.Text(
                                notification.get("created_at", "Just now"),
                                size=13,
                                color=ft.Colors.GREY,
                            ),
                            actions if actions else ft.Container(),
                        ],
                    ),
                    trailing=ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                content="Mark as unread" if is_read else "Mark as read",
                                icon=(
                                    ft.Icons.MARK_EMAIL_UNREAD_OUTLINED
                                    if is_read
                                    else ft.Icons.MARK_EMAIL_READ_OUTLINED
                                ),
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

    #  Mutations                                                          #

    async def toggle_read(self, index: int):
        """Toggles read/unread state for a notification by index."""
        notif = self.notifications[index]
        new_state = not notif.get("is_read", False)

        result = await mark_notification_as_read(notif["id"], is_read=new_state)
        if result.get("success"):
            self.notifications[index]["is_read"] = new_state
            self._emit_badge()

            if self._is_mounted:
                self.notifications_list.controls[index] = self.notif_card(
                    self.notifications[index],
                    index,
                    file=self.notifications[index].get("_file"),
                )
                self.notifications_list.update()

    async def _delete(self, index: int):
        """Deletes a notification and rebuilds the list to fix stale indices."""
        notif = self.notifications[index]
        result = await delete_notification(notif["id"])
        if result.get("success"):
            notif_id = notif.get("id")
            self.notifications.pop(index)
            self.special_notification_ids.pop(notif_id, None)
            self._rebuild_list()

    #  Data loading                                                       #

    async def load_notifications(self, user_id: int):
        """
        Fetches notifications from the API and refreshes state.

        Two call sites:
          1. MainPage.build() finally block via page.run_task() — _is_mounted is
             False at this point, so only the badge gets updated.
          2. open_notifications_page() AFTER build() is appended — _is_mounted is
             True, so the list also renders with fresh data.
        """
        try:
            data = await get_notifications(user_id)
            print(f"[NotificationPage] API response: {data}")

        except Exception as e:
            print(f"[NotificationPage] load_notifications error: {e}")
            return

        self.notifications = data.get("notifications", [])
        print(f"[NotificationPage] loaded {len(self.notifications)} notifications")

        for n in self.notifications:
            if n.get("crack_id"):
                from services.crack_service import fetch_one_crack

                res = await fetch_one_crack(n.get("crack_id"))
                n["_file"] = res.get("crack")

            if n.get("inviter_id"):
                self.special_notification_ids[n["id"]] = n["inviter_id"]

        self._rebuild_list()

    #  WebSocket push handler                                             #

    async def handle_notification(self, data: dict):
        """
        Handles incoming WebSocket push.
        Updates in-memory list and badge immediately.
        If the notification page is open, the ListView refreshes too.
        """
        event = data.get("event")
        notif_id = data.get("notification_id")

        if not notif_id:
            return

        try:
            from services.notification_service import get_notification_by_id

            result = await get_notification_by_id(notif_id)
        except Exception as e:
            print(f"[NotificationPage] handle_notification fetch error: {e}")
            return

        notif = result.get("notification")
        if not notif:
            return

        if event == "new_assignment":
            inviter_id = data.get("inviter_id")
            self.special_notification_ids[notif_id] = inviter_id
            notif["inviter_id"] = inviter_id

        if notif.get("crack_id"):
            from services.crack_service import fetch_one_crack

            res = await fetch_one_crack(notif.get("crack_id"))
            notif["_file"] = res.get("crack")

        self.notifications.insert(0, notif)
        self._rebuild_list()

    #  Actions                                                            #

    async def accept_invitation(self, notification: dict):
        notif_id = notification.get("id")
        inviter_id = self.special_notification_ids.get(notif_id) or notification.get(
            "inviter_id"
        )

        if not inviter_id:
            return

        from services.engineer_service import accept_engineer_invitation

        res = await accept_engineer_invitation(inviter_id, self.user.get("id"))

        if res.get("success"):
            self.special_notification_ids.pop(notif_id, None)
            index = next(
                (
                    i
                    for i, n in enumerate(self.notifications)
                    if n.get("id") == notif_id
                ),
                None,
            )
            delete_result = await delete_notification(notif_id)
            if delete_result.get("success") and index is not None:
                self.notifications.pop(index)
                self._rebuild_list()

    async def view_crack_details(self, notification: dict):
        from services.crack_service import fetch_one_crack

        res = await fetch_one_crack(notification.get("crack_id"))
        file = res.get("crack")
        if file:
            show_full(self.page, file)

        index = next(
            (
                i
                for i, n in enumerate(self.notifications)
                if n.get("id") == notification.get("id")
            ),
            None,
        )
        if index is not None:
            await self.toggle_read(index)
