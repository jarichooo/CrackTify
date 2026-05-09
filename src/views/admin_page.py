import asyncio

import flet as ft

from services.admin_service import (
    approve_verification,
    decline_verification,
    get_pending_verifications,
)
from utils.themes import toggle_theme
from views.template import TemplatePage


# ── Tiny helpers (ported from admin_main.py, now theme-aware) ────────────────

def _chip(label: str, color) -> ft.Container:
    """Coloured pill badge — used for severity / status labels."""
    return ft.Container(
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_600, color=color),
        bgcolor=ft.Colors.with_opacity(0.13, color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.35, color)),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
    )


def _info_row(label: str, value: str) -> ft.Row:
    """Compact  label: value  display row."""
    return ft.Row(
        spacing=6,
        controls=[
            ft.Text(
                f"{label}:",
                size=11,
                color=ft.Colors.OUTLINE,
                weight=ft.FontWeight.W_600,
            ),
            ft.Text(str(value) if value else "—", size=11),
        ],
    )


def _snack(page: ft.Page, msg: str, success: bool = True):
    page.show_snack_bar(ft.SnackBar(
        content=ft.Text(msg, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN if success else ft.Colors.ERROR,
    ))


# ── Dialogs ──────────────────────────────────────────────────────────────────

def _confirm_dialog(page: ft.Page, title: str, body: str, on_confirm):
    """Generic yes/no confirmation dialog."""
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(body),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Confirm",
                bgcolor=ft.Colors.ERROR,
                color=ft.Colors.WHITE,
                on_click=lambda e: (page.pop_dialog(), on_confirm()),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)


def _decline_dialog(page: ft.Page, engineer_name: str, on_confirm):
    """Decline dialog with an optional reason text field."""
    reason_field = ft.TextField(
        label="Reason for declining (optional)",
        hint_text="e.g. Document unclear, license number mismatch…",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=10,
    )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Decline: {engineer_name}"),
        content=ft.Column(
            tight=True,
            spacing=12,
            controls=[
                ft.Text(
                    "The engineer will be notified with your reason.",
                    size=13,
                    color=ft.Colors.OUTLINE,
                ),
                reason_field,
            ],
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Decline",
                bgcolor=ft.Colors.ERROR,
                color=ft.Colors.WHITE,
                on_click=lambda e: (
                    page.pop_dialog(),
                    on_confirm(reason_field.value or ""),
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)


# ── Verification card ─────────────────────────────────────────────────────────

def _verification_card(item: dict, on_approve, on_decline) -> ft.Container:
    """
    Card showing full engineer verification info.
    Fields returned by GET /admin/pending-verifications:
      user, first_name, last_name, email_address,
      public_id, document_url, user_id, license_number, uploaded_at
    """
    public_id      = item.get("public_id", "—")
    engineer_id    = item.get("user_id", "—")
    username       = item.get("user") or "Unknown"
    first_name     = item.get("first_name", "")
    last_name      = item.get("last_name", "")
    email_address  = item.get("email_address", "")
    license_number = item.get("license_number", "")
    document_url   = item.get("document_url", "")
    uploaded_at    = str(item.get("uploaded_at", ""))[:10]
    full_name      = f"{first_name} {last_name}".strip() or username
    avatar_letter  = full_name[0].upper() if full_name else "?"

    return ft.Container(
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=14,
        padding=16,
        margin=ft.margin.only(bottom=12),
        content=ft.Column(
            spacing=12,
            controls=[
                # ── Top row: avatar + name/chip + action buttons ──────
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        # Avatar + name block
                        ft.Row(
                            spacing=12,
                            expand=True,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Text(
                                        avatar_letter,
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color=ft.Colors.WHITE,
                                    ),
                                    bgcolor=ft.Colors.SECONDARY,
                                    radius=22,
                                ),
                                ft.Column(
                                    spacing=3,
                                    expand=True,
                                    controls=[
                                        ft.Text(
                                            full_name,
                                            size=14,
                                            weight=ft.FontWeight.W_700,
                                        ),
                                        ft.Text(
                                            f"@{username}",
                                            size=12,
                                            color=ft.Colors.OUTLINE,
                                        ),
                                        _chip("Pending", ft.Colors.AMBER),
                                    ],
                                ),
                            ],
                        ),
                        # Approve / Decline buttons stacked vertically
                        ft.Column(
                            spacing=6,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.VERIFIED_USER_OUTLINED,
                                                size=14,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Text(
                                                "Approve",
                                                color=ft.Colors.WHITE,
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                    ),
                                    bgcolor=ft.Colors.GREEN,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda e, pid=public_id, eid=engineer_id: on_approve(pid, eid),
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.CANCEL_OUTLINED,
                                                size=14,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Text(
                                                "Decline",
                                                color=ft.Colors.WHITE,
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                    ),
                                    bgcolor=ft.Colors.ERROR,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda e, pid=public_id, eid=engineer_id, name=full_name: on_decline(pid, eid, name),
                                ),
                            ],
                        ),
                    ],
                ),

                ft.Divider(height=1),

                # ── Info grid ─────────────────────────────────────────
                ft.Row(
                    spacing=24,
                    wrap=True,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                _info_row("Email",     email_address),
                                _info_row("User ID",   str(engineer_id)),
                                _info_row("Submitted", uploaded_at),
                            ],
                        ),
                        ft.Column(
                            spacing=5,
                            controls=[
                                _info_row("License #", license_number),
                                _info_row("Public ID", public_id),
                            ],
                        ),
                    ],
                ),

                # ── Document link ──────────────────────────────────────
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(
                            ft.Icons.ATTACH_FILE_OUTLINED,
                            size=13,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            "",
                            spans=[
                                ft.TextSpan(
                                    "View Document →",
                                    style=ft.TextStyle(
                                        color=ft.Colors.PRIMARY,
                                        decoration=ft.TextDecoration.UNDERLINE,
                                    ),
                                    url=document_url,
                                )
                            ],
                        ),
                    ],
                ) if document_url else ft.Container(height=0),
            ],
        ),
    )


# ── Crack card ────────────────────────────────────────────────────────────────

def _crack_card(crack: dict, on_delete) -> ft.Container:
    crack_id    = crack.get("id") or crack.get("_id") or "—"
    filename    = (
        crack.get("filename")
        or crack.get("title")
        or crack.get("name")
        or f"Crack #{crack_id}"
    )
    severity    = crack.get("severity") or crack.get("status") or "Unknown"
    probability = crack.get("probability", 0)
    detected_at = str(
        crack.get("detected_at") or crack.get("created_at") or ""
    )[:10]

    sev_color = {
        "High": ft.Colors.RED,
        "Mild": ft.Colors.AMBER,
        "Low":  ft.Colors.GREEN,
    }.get(severity, ft.Colors.OUTLINE)

    return ft.Container(
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=14,
        padding=16,
        margin=ft.margin.only(bottom=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=14,
                    expand=True,
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                            content=ft.Icon(
                                ft.Icons.BROKEN_IMAGE_OUTLINED,
                                color=ft.Colors.PRIMARY,
                                size=20,
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            spacing=4,
                            expand=True,
                            controls=[
                                ft.Text(
                                    filename,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        _chip(severity, sev_color),
                                        ft.Text(
                                            f"{probability * 100:.1f}%  ·  {detected_at}",
                                            size=11,
                                            color=ft.Colors.OUTLINE,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.ERROR,
                    icon_size=22,
                    tooltip="Delete crack",
                    on_click=lambda e, cid=crack_id: on_delete(cid),
                ),
            ],
        ),
    )


# ── Engineers / Pending Verifications view ────────────────────────────────────

class EngineersView(ft.Column):
    """
    Shows all pending engineer verifications.
    Approve → POST /admin/approve-verification
    Decline → POST /admin/decline-verification  (with optional reason)
    """

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self._page = page
        self._all: list = []

        self.search = ft.TextField(
            hint_text="Search by name, username, email or license…",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            border_color=ft.Colors.SURFACE_TINT,
            width=400,
            on_change=self._filter,
        )

        self.list_view = ft.ListView(
            expand=True, spacing=0, padding=ft.padding.only(top=8)
        )
        self.loading = ft.ProgressRing(width=32, height=32)
        self.empty   = ft.Text(
            "No pending verifications.", color=ft.Colors.OUTLINE, size=14
        )

        self.controls = [
            ft.Container(
                padding=ft.padding.only(bottom=16),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "Pending Verifications",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    icon_color=ft.Colors.PRIMARY,
                                    tooltip="Refresh",
                                    on_click=lambda e: self._page.run_task(self.load),
                                ),
                            ],
                        ),
                        self.search,
                    ],
                ),
            ),
            ft.Container(expand=True, content=self.list_view),
        ]

    # ── Data loading ──────────────────────────────────────────────────────────

    async def load(self):
        self.list_view.controls = [
            ft.Row([self.loading], alignment=ft.MainAxisAlignment.CENTER)
        ]
        self.list_view.update()
        try:
            resp = await get_pending_verifications()
            self._all = resp.get("verifications", [])
            self._filter()
        except Exception as ex:
            _snack(self._page, f"Failed to load: {ex}", success=False)
            self.list_view.controls = []
            self.list_view.update()

    # ── Filtering ─────────────────────────────────────────────────────────────

    def _filter(self, e=None):
        q = (self.search.value or "").lower()
        if q:
            filtered = [
                item for item in self._all
                if q in str(item.get("user", "")).lower()
                or q in str(item.get("first_name", "")).lower()
                or q in str(item.get("last_name", "")).lower()
                or q in str(item.get("email_address", "")).lower()
                or q in str(item.get("license_number", "")).lower()
                or q in str(item.get("public_id", "")).lower()
                or q in str(item.get("user_id", "")).lower()
            ]
        else:
            filtered = list(self._all)
        self._render(filtered)

    def _render(self, items: list):
        if not items:
            self.list_view.controls = [
                ft.Row([self.empty], alignment=ft.MainAxisAlignment.CENTER)
            ]
        else:
            self.list_view.controls = [
                _verification_card(item, self._approve, self._decline)
                for item in items
            ]
        self.list_view.update()

    # ── Approve flow ──────────────────────────────────────────────────────────

    def _approve(self, public_id: str, engineer_id: str):
        _confirm_dialog(
            self._page,
            "Approve Verification",
            f"Approve engineer (ID: {engineer_id})? They will be notified.",
            lambda: self._page.run_task(self._do_approve, public_id, engineer_id),
        )

    async def _do_approve(self, public_id: str, engineer_id: str):
        result = await approve_verification(public_id, engineer_id)
        if result.get("success") is False:
            _snack(self._page, f"Error: {result.get('error', 'Unknown')}", success=False)
        else:
            _snack(self._page, "Engineer approved ✓")
            await self.load()

    # ── Decline flow ──────────────────────────────────────────────────────────

    def _decline(self, public_id: str, engineer_id: str, full_name: str):
        _decline_dialog(
            self._page,
            full_name,
            lambda reason: self._page.run_task(
                self._do_decline, public_id, engineer_id, reason
            ),
        )

    async def _do_decline(self, public_id: str, engineer_id: str, reason: str):
        result = await decline_verification(public_id, engineer_id, reason)
        if result.get("success") is False:
            _snack(self._page, f"Error: {result.get('error', 'Unknown')}", success=False)
        else:
            _snack(self._page, "Verification declined — engineer notified.")
            await self.load()


# # ── Cracks view ───────────────────────────────────────────────────────────────

# class CracksView(ft.Column):
#     """
#     Shows all crack detections across every user.
#     Delete → POST /cracks/delete
#     """

#     def __init__(self, page: ft.Page, token: str):
#         super().__init__(expand=True, spacing=0)
#         self._page = page
#         self.token = token
#         self._all: list = []

#         self.search = ft.TextField(
#             hint_text="Search cracks…",
#             prefix_icon=ft.Icons.SEARCH,
#             border_radius=10,
#             on_change=self._filter,
#         )

#         self.list_view = ft.ListView(
#             expand=True, spacing=0, padding=ft.padding.only(top=8)
#         )
#         self.loading = ft.ProgressRing(width=32, height=32)
#         self.empty   = ft.Text(
#             "No cracks found.", color=ft.Colors.OUTLINE, size=14
#         )

#         self.controls = [
#             ft.Container(
#                 padding=ft.padding.only(bottom=16),
#                 content=ft.Column(
#                     spacing=12,
#                     controls=[
#                         ft.Row(
#                             alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
#                             controls=[
#                                 ft.Text(
#                                     "Cracks Management",
#                                     size=18,
#                                     weight=ft.FontWeight.W_700,
#                                 ),
#                                 ft.IconButton(
#                                     icon=ft.Icons.REFRESH,
#                                     icon_color=ft.Colors.PRIMARY,
#                                     tooltip="Refresh",
#                                     on_click=lambda e: self._page.run_task(self.load),
#                                 ),
#                             ],
#                         ),
#                         self.search,
#                     ],
#                 ),
#             ),
#             ft.Container(expand=True, content=self.list_view),
#         ]

#     # ── Data loading ──────────────────────────────────────────────────────────

#     async def load(self):
#         self.list_view.controls = [
#             ft.Row([self.loading], alignment=ft.MainAxisAlignment.CENTER)
#         ]
#         self.list_view.update()
#         try:
#             resp = await fetch_all_cracks(self.token)
#             self._all = resp.get("cracks", []) if isinstance(resp, dict) else []
#             self._filter()
#         except Exception as ex:
#             _snack(self._page, f"Failed to load cracks: {ex}", success=False)
#             self.list_view.controls = []
#             self.list_view.update()

#     # ── Filtering ─────────────────────────────────────────────────────────────

#     def _filter(self, e=None):
#         q = (self.search.value or "").lower()
#         if q:
#             filtered = [
#                 c for c in self._all
#                 if q in str(c.get("filename", "")).lower()
#                 or q in str(c.get("title", "")).lower()
#                 or q in str(c.get("name", "")).lower()
#                 or q in str(c.get("id", "")).lower()
#                 or q in str(c.get("severity", "")).lower()
#             ]
#         else:
#             filtered = list(self._all)
#         self._render(filtered)

#     def _render(self, cracks: list):
#         if not cracks:
#             self.list_view.controls = [
#                 ft.Row([self.empty], alignment=ft.MainAxisAlignment.CENTER)
#             ]
#         else:
#             self.list_view.controls = [
#                 _crack_card(c, self._delete) for c in cracks
#             ]
#         self.list_view.update()

#     # ── Delete flow ───────────────────────────────────────────────────────────

#     def _delete(self, crack_id):
#         _confirm_dialog(
#             self._page,
#             "Delete Crack",
#             f"Permanently delete crack ID: {crack_id}?",
#             lambda: self._page.run_task(self._do_delete, crack_id),
#         )

#     async def _do_delete(self, crack_id):
#         result = await delete_crack(crack_id, self.token)
#         if result.get("success") is False:
#             _snack(self._page, f"Error: {result.get('error', 'Unknown')}", success=False)
#         else:
#             _snack(self._page, f"Crack {crack_id} deleted.")
#             await self.load()


# ── AdminPage — top-level View ────────────────────────────────────────────────

NAV_ENGINEERS = 0
NAV_CRACKS    = 1


class AdminPage(TemplatePage):
    """
    Top-level admin view, structured like MainPage:
      - ft.AppBar  with admin icon, theme toggle, and a red logout button
      - ft.NavigationBar (bottom) — Engineers | Cracks
      - Body swaps between EngineersView and CracksView

    The JWT token is received from main.py's route_change() and forwarded
    to both sub-views so every API call is authenticated.
    """

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.engineers_view = EngineersView(page)
        self.active_view    = self.engineers_view
        self.prev_index     = NAV_ENGINEERS

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.View:
        self.toggle_theme_button = ft.IconButton(
            icon=(
                ft.Icons.LIGHT_MODE
                if self.page.theme_mode == ft.ThemeMode.LIGHT
                else ft.Icons.DARK_MODE
            ),
            tooltip="Toggle Theme",
            on_click=lambda _: asyncio.create_task(
                toggle_theme(self.page, self.toggle_theme_button)
            ),
        )

        self.app_bar = ft.AppBar(
            leading=ft.Row(
                controls=[
                    ft.Container(width=4),
                    ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=22),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            leading_width=44,
            title=ft.Text("Admin Panel"),
            automatically_imply_leading=False,
            force_material_transparency=True,
            actions=[
                self.toggle_theme_button,
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    icon_color=ft.Colors.ERROR,
                    on_click=self._confirm_logout,
                ),
            ],
        )

        self.body = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            expand=True,
            content=self.active_view,
        )

        self.nav_bar = ft.NavigationBar(
            selected_index=self.prev_index,
            on_change=self._on_nav_change,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.VERIFIED_USER_OUTLINED,
                    selected_icon=ft.Icons.VERIFIED_USER,
                    label="Engineers",
                ),
                # ft.NavigationBarDestination(
                #     icon=ft.Icons.BROKEN_IMAGE_OUTLINED,
                #     selected_icon=ft.Icons.BROKEN_IMAGE,
                #     label="Cracks",
                # ),
            ],
        )

        # Load Engineers view on mount
        self.page.run_task(self.engineers_view.load)

        return self.layout(
            route="/admin",
            appbar=self.app_bar,
            navigation_bar=self.nav_bar,
            controls=ft.Column(
                expand=True,
                controls=[self.body],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ── Navigation ────────────────────────────────────────────────────────────

    def _on_nav_change(self, e):
        index = e.control.selected_index
        if index == self.prev_index:
            return

        self.prev_index = index

        if index == NAV_ENGINEERS:
            self.active_view = self.engineers_view
            self.app_bar.title = ft.Text("Admin Panel")
        else:
            self.active_view = self.cracks_view
            self.app_bar.title = ft.Text("Cracks Management")

        self.app_bar.update()
        self.body.content = self.active_view
        self.body.update()

        # Lazy-load the newly selected view
        self.page.run_task(self.active_view.load)

    # ── Logout ────────────────────────────────────────────────────────────────

    def _confirm_logout(self, e=None):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Logout"),
            content=ft.Text("Are you sure you want to log out of the admin panel?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                ft.ElevatedButton(
                    "Logout",
                    bgcolor=ft.Colors.ERROR,
                    color=ft.Colors.ON_INVERSE_SURFACE,
                    on_click=lambda _: self.page.run_task(self._do_logout),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    async def _do_logout(self):
        self.page.pop_dialog()
        self.show_loading("Logging out…")

        await self.page.shared_preferences.set("auth_token", "")
        await self.page.shared_preferences.set("is_admin", "")

        self.hide_loading()
        await self.page.push_route("/login")