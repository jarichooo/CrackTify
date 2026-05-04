import asyncio
import random
from typing import Generator, List
import flet as ft
import flet_lottie as ftl  # type: ignore
from services.crack_service import fetch_cracks_service
from utils.file_utils import build_thumb
from utils.page_utils import show_full
from utils.time_utils import convert_to_utc8

from model.user import User


class HomeSection:
    async def get_cracks(self):
        res = await fetch_cracks_service(self.user.get("id"))

        if not res.get("success"):
            self.search_body.content = ft.Text(
                "Failed to load files.",
                size=20,
                weight="bold",
                color=ft.Colors.RED,
            )
            self.page.update()
            return []

        return res.get("cracks", [])

    async def load_cracks(self):
        self.recent_cracks = await self.get_cracks()
        self.page.update()

    def __init__(self, page: ft.Page):
        self.page = page
        self.user = User.to_dict()  # Get user data as a dictionary

        # Define header states with text and corresponding Lottie animation URLs
        self.header_states = [
            {
                "text": "Crack the code.\nLevel up your skills.",
                "lottie": "https://lottie.host/b9c2c1c3-251e-4429-84bd-7e01f5494881/04fQlqqIzI.json",
            },
            {
                "text": "Every crack leads\nto discovery.",
                "lottie": "https://lottie.host/dd1339c6-836f-4233-885f-70642daa2a64/PQgmgLrzYI.json",
            },
            {
                "text": "Bird sees cracks.\nYou see possibilities.",
                "lottie": "https://lottie.host/c78f9f1f-dfc2-4a40-b479-ae2a98812a9d/GSFw0u6mJr.json"
            },
            {
                "text": "Building a crack-free world,\none detection at a time.",
                "lottie": "https://lottie.host/94d5a43e-6e6f-466d-b2a6-a44a0604bf37/vfgonGMYvk.json",
            },
            {
                "text": "Cracktify\nyour curiosity.",
                "lottie": "https://lottie.host/b7449fb3-0234-4294-8537-dd8da8863241/Q80p9HiW2S.json",
            },
            {
                "text": "Break the limits.\nFind the crack.",
                "lottie": "https://lottie.host/8949bf4b-3fb2-481c-8900-2a770573497d/d3H80coEST.json",
            },
            {
                "text": "A frog looking for cracks.\nJoin the journey.",
                "lottie": "https://lottie.host/cdc68723-c4e4-4453-8719-f8c892bc527c/ekpwJzFMJE.json"
            },
            {
                "text": "Think deeper.\nCrack smarter.",
                "lottie": "https://lottie.host/0a4df0d8-fc9d-47c1-818b-470a31dd0888/QVKgINrlWC.json",
            },
            {
                "text": "One crack at a time.\nMaster the unknown.",
                "lottie": "https://lottie.host/12a053ab-0a52-41ad-8760-0c2c0b492ac2/sITwjOvf3X.json",
            },
            {
                "text": "A mouse finds its way\nthrough cracks. So will you.",
                "lottie": "https://lottie.host/c5f163ee-bdd5-4aa6-9833-3081b3dbe752/EiZ7MUjUSr.json",
            },
        ]

        # Build header controls
        self.text_control = ft.Text(
            value=self.header_states[0]["text"],
            size=23,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PRIMARY,
            text_align=ft.TextAlign.LEFT,
        )

        self.text_container = ft.Container(
            expand=2,
            content=self.text_control,
            opacity=1,
            offset=ft.Offset(0, 0),
            animate_opacity=400,
            animate_offset=400,
            alignment=ft.Alignment.CENTER_LEFT,
            width=self.page.width * 0.6 if self.page.width else 300,
        )

        self.lottie_control = ftl.Lottie(
            src=self.header_states[0]["lottie"],
            animate=True,
            repeat=True,
            error_content=ft.Icon(ft.Icons.SIGNAL_WIFI_BAD, color=ft.Colors.RED),
            fit=ft.BoxFit.CONTAIN,
        )

        self.lottie_container = ft.Container(
            expand=1,
            content=self.lottie_control,
            height=self.page.height * 0.30 if self.page.height else 240,
            opacity=1,
            offset=ft.Offset(0, 0),
            animate_opacity=400,
            animate_offset=400,
            # right=-20,
            # top=-40,
            alignment=ft.Alignment.CENTER_RIGHT,
            width=self.page.width * 0.4 if self.page.width else 300,
        )

        # Initialize stats and recents data
        self.stats = {}
        self.recent_cracks = []


        # Set initial header state
        self.header_index = random.randint(0, len(self.header_states) - 1)

        state = self.header_states[self.header_index]
        self.text_control.value = state["text"]
        self.lottie_control.src = state["lottie"]

        self.page.run_task(
            self.load_cracks
        )  # Load recent cracks when section is initialized

    def build(self):
        """Build the home section UI."""
        self.header = ft.Container(
            width=self.page.width,
            expand=1,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Row(
                controls=[
                    self.lottie_container,  # Right
                    self.text_container,  # Left
                ],
            ),
        )

        # Start animation loop
        # self.page.run_task(self.rotate_header_loop)

        self.stat_container = ft.Container(
            width=self.page.width,
            expand=1,
            content=ft.Column(
                controls=[
                    ft.Text("Stats", size=20),
                    ft.Row(
                        spacing=10,
                        controls=[
                            self.create_info_tile(
                                "Total",
                                self.stats.get("total_cracks", 0),
                                ft.Colors.with_opacity(0.8, ft.Colors.BLUE_900),
                            ),
                            self.create_info_tile(
                                "High",
                                self.stats.get("total_high_cracks", 0),
                                ft.Colors.with_opacity(0.8, ft.Colors.RED_900),
                            ),
                            self.create_info_tile(
                                "Mild",
                                self.stats.get("total_mild_cracks", 0),
                                ft.Colors.with_opacity(0.8, ft.Colors.YELLOW_900),
                            ),
                            self.create_info_tile(
                                "Low",
                                self.stats.get("total_low_cracks", 0),
                                ft.Colors.with_opacity(0.8, ft.Colors.GREEN_900),
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.recent_list = ft.ListView(
            expand=True,
            spacing=10,
        )

        self.recent_container = ft.Container(
            expand=3,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.ProgressBar(),
        )

        # Body
        self.body = ft.Column(
            controls=[
                self.header,
                self.stat_container,
                ft.Text("Recent", size=20),
                ft.Container(height=10),  # Spacer
                self.recent_container,
            ],
            spacing=0,
        )

        return [self.body]
            
    async def rotate_header_loop(self):
        """Continuously rotate through header states with animation."""
        while True:
            await asyncio.sleep(10)  # Wait before rotating to the next header state
            # Animate OUT
            self.text_container.opacity = 0
            self.text_container.offset = ft.Offset(0, -0.1)
            self.lottie_container.opacity = 0
            self.lottie_container.offset = ft.Offset(0, -0.1)

            self.page.update()
            await asyncio.sleep(0.45)

            # Swap content
            self.header_index = (self.header_index + 1) % len(self.header_states)
            state = self.header_states[self.header_index]

            self.text_control.value = state["text"]
            self.lottie_control.src = state["lottie"]

            # Prepare IN
            self.text_container.offset = ft.Offset(0, 0.1)
            self.lottie_container.offset = ft.Offset(0, 0.1)
            self.page.update()
            await asyncio.sleep(0.05)

            # Animate IN
            self.text_container.opacity = 1
            self.text_container.offset = ft.Offset(0, 0)
            self.lottie_container.opacity = 1
            self.lottie_container.offset = ft.Offset(0, 0)
            self.page.update()

    def refresh(self):
        """Public method to trigger data refresh on the home section."""
        asyncio.create_task(self.lazy_load())

    async def lazy_load(self):
        """Load data for stats and recents."""
        self.recent_container.content = (
            ft.ProgressBar()
        )  # Show loading indicator while fetching data
        self.page.update()

        if self.recent_cracks:
            self.update_home()

        # Fetch in background
        crack_resp = await fetch_cracks_service(self.user.get("id"))

        if not crack_resp.get("success"):
            self.recent_container.content = ft.Text(
                "Failed to load recents.", size=16, color=ft.Colors.RED
            )
            self.page.update()
            return

        # Compare old and new data to determine if UI update is needed
        old_stats = self.stats
        old_recents = self.recent_cracks

        new_stats = crack_resp.get("stats", {})
        new_recents = crack_resp.get("cracks", [])

        top_new_recents = new_recents[
            :4
        ]  # Limit to top 4 recent cracks for the home section

        if (
            new_stats == old_stats
            and top_new_recents == old_recents
            and self.recent_cracks != []
        ):  # if both is equal but not empty, no changes and new feches is not empty
            self.recent_container.content = (
                self.recent_list
            )  # Remove loading indicator if data is the same but not empty
            return  # nothing changed → no UI update

        self.stats = new_stats
        self.recent_cracks = top_new_recents
        self.update_home()

    def update_home(self):
        """Public method to trigger data refresh on the home section."""
        self.recent_list.controls.clear()  # Clear existing recent items

        if not self.recent_cracks:  # If no recents found, show message
            self.recent_container.content = ft.Column(
                controls=[
                    ft.Text("No recents found.", size=16, color=ft.Colors.GREY),
                    ft.Text(
                        "Detect some cracks to see your recent uploads.",
                        size=16,
                        color=ft.Colors.GREY,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
            return

        for crack in self.recent_cracks:
            # Extract relevant info with fallbacks
            filename = crack.get("filename", "Unknown File")
            severity = crack.get("severity", "Unknown Severity")
            probability = crack.get("probability", 0)
            date_str = convert_to_utc8(crack.get("detected_at", ""))

            date = date_str.split("T")[0] if "T" in date_str else date_str
            time = date_str.split("T")[1].split(".")[0] if "T" in date_str else ""

            thumb_image = build_thumb(crack, with_playbtn=False)
            thumb_image.on_click = lambda _, file=crack: show_full(self.page, file, refresh_function=self.refresh)

            bgcolor = (
                ft.Colors.GREEN
                if severity == "Low"
                else (
                    ft.Colors.YELLOW
                    if severity == "Mild"
                    else ft.Colors.RED if severity == "High" else ft.Colors.GREEN
                )
            )

            self.recent_list.controls.append(
                ft.ListTile(
                    leading=thumb_image,
                    title=ft.Column(
                        controls=[
                            ft.Text(
                                filename,
                                size=16,
                                weight="bold",
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"Severity: {severity} ({probability*100:.1f}%)",
                                size=14,
                            ),
                        ],
                        width=250,
                        spacing=2,
                    ),
                    subtitle=ft.Text(
                        f"Uploaded on {date} at {time}", size=12, color=ft.Colors.GREY
                    ),
                    is_three_line=True,
                    bgcolor=ft.Colors.with_opacity(0.1, bgcolor),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    on_click=lambda _, file=crack: show_full(self.page, file, refresh_function=self.refresh),
                )
            )

        self.recent_container.content = (
            self.recent_list
        )  # Set the recent container content to the updated list
        self.update_stats()  # Update stats section as well
        self.page.update()

    def create_info_tile(self, title, value, bg_color):
        return ft.Container(
            padding=10,
            expand=1,
            bgcolor=bg_color,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[
                    ft.Text(str(value), size=18, weight="bold", color=ft.Colors.WHITE),
                    ft.Text(title, size=14, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        )

    def update_stats(self):
        """Update the stats section with current data."""

        self.stat_container.content.controls[1] = ft.Row(
            spacing=10,
            controls=[
                self.create_info_tile(
                    "Total",
                    self.stats.get("total_cracks", 0),
                    ft.Colors.with_opacity(0.8, ft.Colors.BLUE_900),
                ),
                self.create_info_tile(
                    "High",
                    self.stats.get("total_high_cracks", 0),
                    ft.Colors.with_opacity(0.8, ft.Colors.RED_900),
                ),
                self.create_info_tile(
                    "Mild",
                    self.stats.get("total_mild_cracks", 0),
                    ft.Colors.with_opacity(0.8, ft.Colors.YELLOW_900),
                ),
                self.create_info_tile(
                    "Low",
                    self.stats.get("total_low_cracks", 0),
                    ft.Colors.with_opacity(0.8, ft.Colors.GREEN_900),
                ),
            ],
        )
