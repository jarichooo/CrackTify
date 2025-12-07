import flet as ft
from typing import List
from pathlib import Path

from services.activity_service import fetch_recent_activity_service
from utils.image_utils import base64_to_image

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = self.page.client_storage.get("user_info") or {}

        self.user_id = self.user.get("id")
        self.first_name = self.user.get("first_name", "User")
        avatar_base64 = self.user.get("avatar_base64")

        # Make sure path exists
        avatar_dir = Path(__file__).parent.parent.parent.parent / "storage" / "images" / "avatars"
        avatar_dir.mkdir(parents=True, exist_ok=True)

        avatar_path = avatar_dir / f"user_{self.user_id}_avatar.png"

        # Save avatar to disk
        self.avatar_path = None
        if avatar_base64:
            self.avatar_path = base64_to_image(avatar_base64, avatar_path)

        # Stats
        self.stats = {
            "stat_1": 0,
            "stat_2": 0
        }

        self.grid: ft.GridView | None = None
        self.activity_list: ft.ListView | None = None

    # MAIN BUILD
    def build(self) -> List[ft.Control]:

        # HEADER CARD
        header_card = ft.Container(
            padding=20,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.BLACK12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text(f"Welcome back, {self.first_name}!", size=18, weight="bold"),
                            ft.Text("Here’s a summary of your activity.",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY)
                        ]
                    ),
                    ft.CircleAvatar(
                        radius=28,
                        foreground_image_src=str(self.avatar_path) if self.avatar_path else None,
                        bgcolor=ft.Colors.BLUE_200,
                    )
                ]
            )
        )

        # QUICK STATS GRID
        self.grid = ft.GridView(
            expand=False,
            runs_count=2,         # 2 columns look better
            max_extent=160,
            spacing=12,
            run_spacing=12,
        )
        self.load_tiles()

        # RECENT ACTIVITY LIST
        self.activity_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=0,
        )

        # Load async data
        self.page.run_task(self.load_recent_activity)
        self.page.run_task(self.load_stats)

        # MAIN PAGE LAYOUT
        return [
            ft.Column(
                spacing=20,
                controls=[
                    header_card,
                    ft.Text("Overview", size=18, weight="bold"),
                    ft.Container(content=self.grid, height=160),
                    ft.Text("Recent Activity", size=18, weight="bold"),
                    ft.Container(content=self.activity_list, height=300)
                ]
            )
        ]

    # TILE COMPONENT
    def info_tile(self, title: str, value: int, icon, color=ft.Colors.SECONDARY_CONTAINER):
        return ft.Container(
            padding=12,
            border_radius=16,
            bgcolor=color,
            shadow=ft.BoxShadow(blur_radius=1, color=ft.Colors.BLACK12),
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
                    ft.Text(title, size=13, weight="bold"),
                    ft.Text(str(value), size=14, weight="w900")
                ]
            )
        )

    # LOAD STAT CARDS
    def load_tiles(self):
        if not self.grid:
            return

        self.grid.controls.clear()

        self.grid.controls.append(
            self.info_tile("stat_1", self.stats["stat_1"], ft.Icons.SEARCH)
        )

        self.grid.controls.append(
            self.info_tile("stat_2", self.stats["stat_2"], ft.Icons.DESCRIPTION)
        )

    # ASYNC LOAD STATS
    async def load_stats(self):
        # Replace with real API later
        self.stats["stat_1"] = 14
        self.stats["stat_2"] = 5

        self.load_tiles()
        self.page.update()

        # Fetch recent activity (wrapper for actual API)
    
    @classmethod
    async def fetch_recent_activity(cls, user_id):
        """Fetch recent activity (wrapper for actual API)"""
        return await fetch_recent_activity_service(user_id)
    
    # ASYNC LOAD RECENT ACTIVITY
    async def load_recent_activity(self):
        
        activities = await self.fetch_recent_activity(self.user.get("id"))
        
        if not activities.get("activities"):
            # No activities returned; clear list and show placeholder
            if self.activity_list:
                self.activity_list.controls.clear()
                self.activity_list.controls.append(
                    ft.Text("No recent activity available.", color=ft.Colors.BLUE_GREY)
                )
                self.page.update()
            return

        # Ensure activities is a list
        if isinstance(activities, str):
            import json
            try:
                activities = json.loads(activities)
            except Exception:
                activities = []

        if not isinstance(activities, list):
            activities = []

        # Clear existing controls
        if self.activity_list:
            self.activity_list.controls.clear()

            for act in activities:
                # Only process dict items
                if not isinstance(act, dict):
                    continue

                severity_color = ft.Colors.RED if act.get("severity") == "Critical" else (
                    ft.Colors.ORANGE if act.get("severity") == "Moderate" else ft.Colors.GREEN
                )

                item = ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    content=ft.Column([
                        ft.Text(f"{act.get('title', 'No title')} in {act.get('group', 'Unknown')}", size=14, weight="bold"),
                        ft.Row([
                            ft.Text(f"Severity: {act.get('severity', '-')}", color=severity_color),
                            ft.Text(f"Time: {act.get('time', '-')}", color=ft.Colors.BLUE_GREY)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
                self.activity_list.controls.append(item)

            self.page.update()


