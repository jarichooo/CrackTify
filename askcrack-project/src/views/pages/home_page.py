import flet as ft
from typing import List
from pathlib import Path

from services.activity_service import fetch_recent_activity_service
from utils.image_utils import base64_to_image

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page

        # Stats
        self.stats = {
            "Detected Cracks": 0,
            "Severe Cracks": 0,
            "Mild Cracks": 0,
            "No Cracks": 0,
        }

        self.grid: ft.GridView | None = None
        self.activity_list: ft.ListView | None = None
        self.activities = {}

    async def fetch_recent_activity(self):
        """Fetch recent activity (wrapper for actual API)"""
        return await fetch_recent_activity_service(self.user_id)

    # MAIN BUILD
    def build(self) -> List[ft.Control]:
        self.user = self.page.client_storage.get("user_info")

        self.user_id = self.user.get("id")
        self.first_name = self.user.get("first_name", "User")
        self.avatar_base64 = self.user.get("avatar_base64")
        

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
                    ft.Container(
                        width=50,
                        height=50,
                        border_radius=50,  # half of width/height for perfect circle-like round image
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src_base64=self.avatar_base64,
                            fit=ft.ImageFit.COVER,
                        )
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

        # RECENT ACTIVITY LIST
        self.activity_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=0,
        )

        # Load async data
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
            self.info_tile("Detected Cracks", self.stats["Detected Cracks"], ft.Icons.SEARCH)
        )

        self.grid.controls.append(
            self.info_tile("Severe Cracks", self.stats["Severe Cracks"], ft.Icons.WARNING)
        )

        self.grid.controls.append(
            self.info_tile("Mild Cracks", self.stats["Mild Cracks"], ft.Icons.INFO)
        )

        self.grid.controls.append(
            self.info_tile("No Cracks", self.stats["No Cracks"], ft.Icons.CHECK_CIRCLE)
        )


    # ASYNC LOAD STATS
    async def load_stats(self):
        self.activities = await self.fetch_recent_activity()

        print("Fetched activities:", self.activities)

        self.stats["Detected Cracks"] = self.activities.get("overview", {}).get("total_cracks", 0)
        self.stats["Severe Cracks"] = self.activities.get("overview", {}).get("total_severe_cracks", 0)
        self.stats["Mild Cracks"] = self.activities.get("overview", {}).get("total_mild_cracks", 0)
        self.stats["No Cracks"] = self.activities.get("overview", {}).get("total_none_cracks", 0)

        self.load_tiles()
        await self.load_recent_activity()

        self.page.update()
    
    # ASYNC LOAD RECENT ACTIVITY
    async def load_recent_activity(self):
        
        if not self.activities.get("activities"):
            # No activities returned; clear list and show placeholder
            if self.activity_list:
                self.activity_list.controls.clear()
                self.activity_list.controls.append(
                    ft.Text("No recent activity available.", color=ft.Colors.BLUE_GREY)
                )
                self.page.update()
            return


        # Clear existing controls
        if self.activity_list:
            self.activity_list.controls.clear()

            for act in self.activities.get("activities", []):
                if act.get("severity") == "Severe":
                    severity_color = ft.Colors.RED  
                elif act.get("severity") == "Mild":
                    severity_color = ft.Colors.ORANGE
                else:
                    severity_color = ft.Colors.GREEN
                
                item = ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    content=ft.Column([
                        ft.Text(f"{act.get("type", "Activity")} in {act.get("location", "Unknown location")}" , size=14, weight="bold", color=ft.Colors.PRIMARY),
                        ft.Row([
                            ft.Text(
                                f"Severity: {act.get('severity', '-')}",
                                color=severity_color
                            ),
                            ft.Text(
                                f"{act.get('time_ago', 'Unknown time')}",
                                color=ft.Colors.BLUE_GREY,
                                italic=True
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
                self.activity_list.controls.append(item)

            self.page.update()




