import flet as ft
from typing import List

# Dummy function for fetching recent activity
async def fetch_recent_activity(user_id):
    # Replace with real API call
    return [
        {"title": "Crack detected", "group": "Group A", "severity": "Critical", "time": "Today"},
        {"title": "Image uploaded", "group": "Group B", "severity": "Moderate", "time": "Yesterday"},
        {"title": "Report generated", "group": "Group C", "severity": "Low", "time": "2 days ago"},
        {"title": "Crack detected", "group": "Group D", "severity": "Moderate", "time": "Today"},
        {"title": "Report generated", "group": "Group E", "severity": "Low", "time": "Yesterday"},
    ]

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = self.page.client_storage.get("user_info")
        self.user_name = self.user.get("fullname", "User")
        self.avatar = self.user.get("avatar", None)

        # Only Detections and Reports
        self.stats = {
            "detections": 0,
            "reports": 0
        }

        self.grid: ft.GridView | None = None
        self.activity_list: ft.ListView | None = None

    def build(self) -> List[ft.Control]:
        # HEADER
        header_card = ft.Container(
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.BLACK12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text(f"Welcome back, {self.user_name}!", size=18, weight="bold"),
                            ft.Text("Here’s a summary of your activity.", size=14, color=ft.Colors.BLUE_GREY)
                        ]
                    ),
                    ft.CircleAvatar(
                        radius=28,
                        foreground_image_src=self.avatar if self.avatar else None,
                        bgcolor=ft.Colors.BLUE_200
                    )
                ]
            )
        )

        # QUICK STATS GRID
        self.grid = ft.GridView(
            expand=False,           # don't expand vertically
            runs_count=1,           # single row
            max_extent=160,         # smaller cards
            spacing=12,
            run_spacing=12,
        )
        self.load_tiles()

        # RECENT ACTIVITY
        self.activity_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=ft.padding.all(0),
        )

        # Async fetch recent activity
        self.page.run_task(self.load_recent_activity)
        self.page.run_task(self.load_stats)

        # MAIN LAYOUT
        return [
            ft.Column(
                spacing=20,
                controls=[
                    header_card,
                    ft.Text("Overview", size=18, weight="bold"),
                    ft.Container(
                        content=self.grid,
                        height=130  # fixed height for the grid
                    ),
                    ft.Text("Recent Activity", size=18, weight="bold"),
                    ft.Container(
                        content=self.activity_list,
                        height=280  # limit height and allow vertical scrolling
                    )
                ]
            )
        ]

    # TILE COMPONENT
    def info_tile(self, title: str, value: int, icon, color=ft.Colors.SECONDARY_CONTAINER):
        return ft.Container(
            width=140,
            padding=12,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.BLACK12),
            bgcolor=color,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        padding=10,
                        bgcolor=ft.Colors.BLUE_50,
                        shape=ft.BoxShape.CIRCLE,
                        content=ft.Icon(icon, size=24, color=ft.Colors.BLUE)
                    ),
                    ft.Text(title, size=13, weight="bold", text_align="center"),
                    ft.Text(str(value), size=14, weight="w900")
                ]
            )
        )

    # LOAD TILES
    def load_tiles(self):
        if not self.grid:
            return
        self.grid.controls.clear()
        self.grid.controls.append(self.info_tile("Detections", self.stats["detections"], ft.Icons.SEARCH))
        self.grid.controls.append(self.info_tile("Reports", self.stats["reports"], ft.Icons.DESCRIPTION))

    # ASYNC LOAD STATS
    async def load_stats(self):
        # Replace with real API calls
        self.stats["detections"] = 14
        self.stats["reports"] = 7
        self.load_tiles()
        self.page.update()

    # ASYNC LOAD RECENT ACTIVITY
    async def load_recent_activity(self):
        activities = await fetch_recent_activity(self.user.get("id"))
        self.activity_list.controls.clear()
        for act in activities:
            severity_color = ft.Colors.RED if act["severity"] == "Critical" else (
                ft.Colors.ORANGE if act["severity"] == "Moderate" else ft.Colors.GREEN
            )
            item = ft.Container(
                padding=15,
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                content=ft.Column([
                    ft.Text(f"{act['title']} in {act['group']}", size=14, weight="bold"),
                    ft.Row([
                        ft.Text(f"Severity: {act['severity']}", color=severity_color),
                        ft.Text(f"Time: {act['time']}", color=ft.Colors.BLUE_GREY)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
            self.activity_list.controls.append(item)
        self.page.update()
