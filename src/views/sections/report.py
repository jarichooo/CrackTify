import asyncio
import datetime
from typing import List

import flet as ft
from services.crack_service import fetch_cracks_service
from services.profile_service import get_associated_user
from utils.file_utils import build_thumb
from utils.page_utils import show_full
from utils.time_utils import convert_to_utc8

from model.user import User

class ReportSection:
    def __init__(self, page):
        self.page = page
        self.user = User.to_dict()

        # List of {id, name} dicts the engineer can access
        self.assigned_users: list[dict] = []

        get_users_task = asyncio.create_task(get_associated_user(self.user.get("id", 0)))
        get_users_task.add_done_callback(self._on_user_ready)

        self.all_cracks: list[dict] = []
        self.filtered_cracks: list[dict] = []

        self.current_filter = "All"
        self.current_sort = "Date Descending"
        self.current_group = "User"

    def build(self) -> List[ft.Control]:
        filter_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Filter By"), ft.Icon(ft.Icons.FILTER_LIST)]),
            items=[
                ft.PopupMenuItem(content="All",  on_click=lambda _: self.change_filter("All")),
                ft.PopupMenuItem(content="High", on_click=lambda _: self.change_filter("High")),
                ft.PopupMenuItem(content="Mild", on_click=lambda _: self.change_filter("Mild")),
                ft.PopupMenuItem(content="Low",  on_click=lambda _: self.change_filter("Low")),
            ],
        )

        sort_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Sort By"), ft.Icon(ft.Icons.SORT)]),
            items=[
                ft.PopupMenuItem(content="Date Descending", on_click=lambda _: self.change_sort("Date Descending")),
                ft.PopupMenuItem(content="Date Ascending",  on_click=lambda _: self.change_sort("Date Ascending")),
                ft.PopupMenuItem(content="Severity",        on_click=lambda _: self.change_sort("Severity")),
                ft.PopupMenuItem(content="Probability",     on_click=lambda _: self.change_sort("Probability")),
            ],
        )

        group_popup = ft.PopupMenuButton(
            content=ft.Row([ft.Text("Group By"), ft.Icon(ft.Icons.GROUP_WORK)]),
            items=[
                ft.PopupMenuItem(content="User",     on_click=lambda _: self.change_group("User")),
                ft.PopupMenuItem(content="Date",     on_click=lambda _: self.change_group("Date")),
                ft.PopupMenuItem(content="Severity", on_click=lambda _: self.change_group("Severity")),
            ],
        )

        self.top_bar = ft.Container(
            content=ft.Row(
                controls=[filter_popup, sort_popup, group_popup],
                alignment=ft.MainAxisAlignment.END,
                spacing=20,
            )
        )

        self.report_list = ft.ListView(expand=True, spacing=8)

        self.body = ft.Container(expand=True, content=ft.Column())

        asyncio.create_task(self.lazy_load())

        return [self.body]

    def refresh(self):
        asyncio.create_task(self.lazy_load())

    async def lazy_load(self):
        self.body.content = ft.ProgressRing()
        self.page.update()

        # Show stale data immediately while re-fetching
        if self.all_cracks:
            self.update_report()

        if not self.assigned_users:
            self.body.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY),
                    ft.Text("No assigned users found.", size=16, color=ft.Colors.GREY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return

        # Fetch all assigned users concurrently
        results = await asyncio.gather(
            *[fetch_cracks_service(u["id"]) for u in self.assigned_users],
            return_exceptions=True,
        )

        merged = []
        for user, res in zip(self.assigned_users, results):
            if isinstance(res, Exception) or not res.get("success"):
                continue
            for crack in res.get("cracks", []):
                firstname = user.get("first_name", "")
                lastname = user.get("last_name", "")
                crack["_username"] = f"{firstname} {lastname}".strip() or user.get("id", "")
                merged.append(crack)

        if merged == self.all_cracks and self.all_cracks:
            return  # nothing changed

        self.all_cracks = merged
        self.filtered_cracks = merged
        self.update_report()

    def change_filter(self, filter_by: str):
        self.current_filter = filter_by
        self.filtered_cracks = [
            c for c in self.all_cracks
            if filter_by == "All" or c.get("severity") == filter_by
        ]
        self.update_report()

    def change_sort(self, sort: str):
        self.current_sort = sort
        self.update_report()

    def change_group(self, group: str):
        self.current_group = group
        self.update_report()

    def update_report(self):
        self.report_list.controls.clear()

        if not self.all_cracks:
            self.body.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ASSESSMENT, size=64, color=ft.Colors.GREY),
                    ft.Text("No reports found.", size=16, color=ft.Colors.GREY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return

        if not self.filtered_cracks:
            self.body.content = ft.Column(
                controls=[
                    self.top_bar,
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.SEARCH_OFF, size=64, color=ft.Colors.GREY),
                                ft.Text("No cracks match the filter.", size=16, color=ft.Colors.GREY),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
                expand=True,
            )
            self.page.update()
            return

        # Sort
        if self.current_sort == "Date Descending":
            cracks = sorted(self.filtered_cracks, key=lambda c: c.get("detected_at", ""), reverse=True)
        elif self.current_sort == "Date Ascending":
            cracks = sorted(self.filtered_cracks, key=lambda c: c.get("detected_at", ""))
        elif self.current_sort == "Severity":
            order = {"High": 0, "Mild": 1, "Low": 2}
            cracks = sorted(self.filtered_cracks, key=lambda c: order.get(c.get("severity", ""), 99))
        elif self.current_sort == "Probability":
            cracks = sorted(self.filtered_cracks, key=lambda c: c.get("probability", 0), reverse=True)
        else:
            cracks = self.filtered_cracks

        # Group and render
        groups: dict[str, list] = {}
        for crack in cracks:
            if self.current_group == "User":
                key = crack.get("_username", "Unknown User")
            elif self.current_group == "Date":
                date_str = convert_to_utc8(crack.get("detected_at", ""))
                raw_date = date_str.split("T")[0] if "T" in date_str else date_str
                try:
                    key = datetime.datetime.strptime(raw_date, "%Y-%m-%d").strftime("%B %d, %Y")
                except ValueError:
                    key = raw_date
            else:  # Severity
                key = crack.get("severity", "Unknown")

            groups.setdefault(key, []).append(crack)

        # Preserve severity order when grouped by severity
        if self.current_group == "Severity":
            key_order = ["High", "Mild", "Low", "Unknown"]
            ordered_groups = {k: groups[k] for k in key_order if k in groups}
        else:
            ordered_groups = dict(sorted(groups.items()))

        for group_name, group_cracks in ordered_groups.items():
            # Group header
            self.report_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(group_name, size=13, weight="bold"),
                            ft.Container(
                                content=ft.Text(str(len(group_cracks)), size=11, color=ft.Colors.WHITE, weight="bold"),
                                bgcolor=ft.Colors.PRIMARY,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(left=4, top=10, bottom=4),
                )
            )

            for crack in group_cracks:
                filename    = crack.get("filename", "Unknown File")
                severity    = crack.get("severity", "Unknown")
                probability = crack.get("probability", 0)
                username    = crack.get("_username", "Unknown User")
                date_str    = convert_to_utc8(crack.get("detected_at", ""))
                date        = date_str.split("T")[0] if "T" in date_str else date_str
                time        = date_str.split("T")[1].split(".")[0] if "T" in date_str else ""

                color = {"High": ft.Colors.RED, "Mild": ft.Colors.YELLOW, "Low": ft.Colors.GREEN}.get(severity, ft.Colors.GREY)

                thumb = build_thumb(crack, with_playbtn=False)
                thumb.on_click = lambda _, f=crack: show_full(self.page, f, refresh_function=self.refresh)

                self.report_list.controls.append(
                    ft.ListTile(
                        leading=thumb,
                        title=ft.Text(filename, size=14, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        subtitle=ft.Column(
                            controls=[
                                ft.Text(f"{severity} — {probability * 100:.1f}%", size=13),
                                ft.Text(f"{username}  ·  {date} {time}", size=12, color=ft.Colors.GREY),
                            ],
                            spacing=2,
                        ),
                        is_three_line=True,
                        bgcolor=ft.Colors.with_opacity(0.07, color),
                        shape=ft.RoundedRectangleBorder(radius=10),
                        on_click=lambda _, f=crack: show_full(self.page, f, refresh_function=self.refresh),
                    )
                )

        self.body.content = ft.Column(
            controls=[self.top_bar, self.report_list],
            expand=True,
        )
        self.page.update()

    def _on_user_ready(self, t: asyncio.Task):
        self.assigned_users = t.result().get("associated_users", [])
        self.refresh()