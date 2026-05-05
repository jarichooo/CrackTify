from widgets.buttons import PrimaryButton, SecondaryButton
from .template import TemplatePage
from services.notification_service import get_notifications, get_notification_by_id, mark_notification_as_read, delete_notification
from utils.file_utils import build_thumb
from utils.page_utils import show_full
import flet as ft
from model.user import User


class NotificationPage(TemplatePage):
    def __init__(self, page: ft.Page, on_back: callable = None):
        super().__init__(page)
        self.user = User.to_dict()  # Get user data as a dictionary
        self.on_back = on_back
        self.notifications = []
        # Maps notification_id -> inviter_id for new_assignment events
        self.special_notification_ids: dict[int, int] = {}

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

    def notif_card(self, notification: dict, index: int, file: dict | None = None) -> ft.Card:
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
                            on_click=lambda e, n=notification: self.page.run_task(self.accept_invitation, n),
                        ),
                        SecondaryButton(
                            "Ignore",
                            color=ft.Colors.GREY,
                            on_click=lambda e, i=index: self.page.run_task(self.toggle_read, i),
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
                        if file else
                        ft.Icon(
                            notification.get("icon", ft.Icons.NOTIFICATIONS_OUTLINED),
                            size=32,
                            color=icon_color,
                        )
                    ),
                    subtitle=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(notification.get("message", "No Message"), max_lines=3),
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
                                icon=ft.Icons.MARK_EMAIL_UNREAD_OUTLINED if is_read else ft.Icons.MARK_EMAIL_READ_OUTLINED,
                                on_click=lambda e, i=index: self.page.run_task(self.toggle_read, i),
                            ),
                            ft.PopupMenuItem(),  # divider
                            ft.PopupMenuItem(
                                content="Delete",
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e, i=index: self.page.run_task(self._delete, i),
                            ),
                        ],
                    ),
                ),
            ),
        )

    def _rebuild_list(self):
        """Rebuild all cards with correct indices. Always call after mutations."""
        self.notifications_list.controls = [
            self.notif_card(n, i, file=n.get("_file"))
            for i, n in enumerate(self.notifications)
        ]
        self.notifications_list.update()

    async def toggle_read(self, index: int):
        """Toggles read/unread state for a notification by index."""
        notif = self.notifications[index]
        new_state = not notif.get("is_read", False)

        result = await mark_notification_as_read(notif["id"], is_read=new_state)
        if result.get("success"):
            self.notifications[index]["is_read"] = new_state
            # Only this card needs rebuilding — indices unchanged
            self.notifications_list.controls[index] = self.notif_card(
                self.notifications[index], index, file=self.notifications[index].get("_file")
            )
            self.notifications_list.update()

    async def _delete(self, index: int):
        """Deletes a notification and rebuilds the list to fix stale indices."""
        notif = self.notifications[index]
        result = await delete_notification(notif["id"])
        if result.get("success"):
            notif_id = notif.get("id")
            self.notifications.pop(index)
            self.special_notification_ids.pop(notif_id, None)  # clean up if special
            self._rebuild_list()

    async def load_notifications(self, user_id: int):
        """Loads notifications from the API on page open."""
        data = await get_notifications(user_id)
        self.notifications = data.get("notifications", [])

        for n in self.notifications:
            # Resolve file thumbnail if linked to a crack
            if n.get("crack_id"):
                from services.crack_service import fetch_one_crack
                res = await fetch_one_crack(n.get("crack_id"))
                n["_file"] = res.get("crack")  # cache on the notification dict

            # Restore special notification tracking from persisted inviter_id
            if n.get("inviter_id"):
                self.special_notification_ids[n["id"]] = n["inviter_id"]

        self._rebuild_list()

    async def handle_notification(self, data: dict):
        """Handles incoming WebSocket push."""
        event = data.get("event")

        if event == "new_assignment":
            notif_id = data.get("notification_id")
            inviter_id = data.get("inviter_id")

            self.special_notification_ids[notif_id] = inviter_id

            from services.notification_service import get_notification_by_id
            result = await get_notification_by_id(notif_id)
            notif = result.get("notification")

            if notif:
                notif["inviter_id"] = inviter_id
                self.notifications.insert(0, notif)
                self._rebuild_list()

        else:
            # For unknown events, fetch the notification and prepend it
            notif_id = data.get("notification_id")
            if notif_id:
                from services.notification_service import get_notification_by_id
                result = await get_notification_by_id(notif_id)
                notif = result.get("notification")
                if notif:
                    self.notifications.insert(0, notif)
                    self._rebuild_list()

    # async def handle_notification(self, data: dict):
    #     """Handles incoming WebSocket push."""
    #     event = data.get("event")

    #     if event == "new_assignment":
    #         notif_id = data.get("notification_id")
    #         inviter_id = data.get("inviter_id")

    #         # Track inviter_id mapped to notification_id
    #         self.special_notification_ids[notif_id] = inviter_id

    #         # Fetch the full notification object since WS only sends ids
    #         from services.notification_service import get_notification_by_id
    #         result = await get_notification_by_id(notif_id)
    #         notif = result.get("notification")

    #         if notif:
    #             notif["inviter_id"] = inviter_id  # attach so it's available at click-time
    #             self.notifications.insert(0, notif)
    #             self._rebuild_list()

    #     elif event == "approved_verification":
    #         # TODO: handle approved verification
    #         pass

    #     elif event == "declined_verification":
    #         # TODO: handle declined verification
    #         pass

    #     else:
    #         # For other events, just refresh the list
    #         await self.load_notifications(self.user.get("id"))

    async def accept_invitation(self, notification: dict):
        """Called when engineer taps Accept on a new_assignment card."""
        notif_id = notification.get("id")

        # Look up the inviter_id we stored at event-time
        inviter_id = self.special_notification_ids.get(notif_id) or notification.get("inviter_id")

        if not inviter_id:
            return  # nothing to do — inviter lost

        from services.profile_service import accept_invitation
        res = await accept_invitation(inviter_id, self.user.get("id"))

        if res.get("success"):
            # Remove from special set so Accept/Ignore buttons disappear
            self.special_notification_ids.pop(notif_id, None)
            # Mark as read and refresh the card
            index = next((i for i, n in enumerate(self.notifications) if n.get("id") == notif_id), None)
            delete_result = await delete_notification(notif_id)  # clean up the notification after accepting
            if delete_result.get("success") and index is not None:
                self.notifications.pop(index)
                self._rebuild_list()
                
            if index is not None:
                await self.toggle_read(index)

    async def view_crack_details(self, notification: dict):
        """Opens the full crack view for crack-linked notifications."""
        from services.crack_service import fetch_one_crack
        res = await fetch_one_crack(notification.get("crack_id"))
        file = res.get("crack")
        if file:
            show_full(self.page, file)

        # Mark as read after viewing
        index = next((i for i, n in enumerate(self.notifications) if n.get("id") == notification.get("id")), None)
        if index is not None:
            await self.toggle_read(index)