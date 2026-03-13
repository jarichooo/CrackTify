import datetime
import flet as ft

from views.template import TemplatePage
from services.crack_service import fetch_cracks_service
from utils.file_utils import build_thumb
from utils.page_utils import show_full
from utils.time_utils import convert_to_utc8

class HistorySection(TemplatePage):
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
        self.crack_files = await self.get_cracks()
        self.page.update()

    def __init__(self, page: ft.Page, user):
        super().__init__(page)
        self.user = user

        self.crack_files = []

        # Schedule async task to load cracks when section is initialized
        self.page.run_task(self.load_cracks)

    def build(self) -> ft.View:
        """Builds the history Page layout."""
        self.history_list = ft.ListView(expand=True, spacing=10)

        self.history_body = ft.Container(
            alignment=ft.Alignment.CENTER, expand=True, content=self.history_list
        )

        return [self.history_body]

    async def lazy_load(self):
        """Fetches and displays the user's crack history."""
        self.history_body.content = (
            ft.ProgressRing()
        )  # Show loading indicator while fetching data
        self.page.update()

        if self.crack_files:
            self.update_history()

        # Fetch in background
        res = await fetch_cracks_service(self.user.get("id"))

        if not res.get("success"):
            self.history_body.content = ft.Text(
                "Failed to load history.", size=20, weight="bold", color=ft.Colors.RED
            )
            self.page.update()
            return

        new_files = res.get("cracks", [])

        #  Compare IDs
        old_ids = {f["id"] for f in self.crack_files}
        new_ids = {f["id"] for f in new_files}

        if (
            new_ids == old_ids and self.crack_files != []
        ):  # if both is equal but not empty, no changes and new feches is not empty
            print("History: No changes in files.")
            return  # nothing changed → no UI update

        self.crack_files = new_files
        self.update_history()

    def update_history(self):
        """Updates the history list with the current files."""

        self.history_list.controls.clear()

        if not self.crack_files:  # If no history found, show message
            self.history_body.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.HISTORY, size=64, color=ft.Colors.GREY),
                    ft.Text("No history found.", size=16, color=ft.Colors.GREY),
                    ft.Text(
                        "Detect some cracks to see history.",
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

        current_date = ""

        cracks = sorted(
            self.crack_files, key=lambda c: c.get("detected_at", ""), reverse=True
        )

        for crack in cracks:
            # Extract relevant info with fallbacks
            filename = crack.get("filename", "Unknown File")
            severity = crack.get("severity", "Unknown Severity")
            probability = crack.get("probability", 0)
            date_str = convert_to_utc8(crack.get("detected_at", ""))

            date = date_str.split("T")[0] if "T" in date_str else date_str
            time = date_str.split("T")[1].split(".")[0] if "T" in date_str else ""

            if date != current_date:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                date_in_words = date_obj.strftime("%B %d, %Y")
                self.history_list.controls.append(ft.Text(date_in_words, size=16))
                current_date = date

            thumb_image = build_thumb(crack, with_playbtn=False)
            thumb_image.on_click = lambda _, file=crack: show_full(self.page, file)

            bgcolor = (
                ft.Colors.GREEN
                if severity == "Low"
                else (
                    ft.Colors.YELLOW
                    if severity == "Mild"
                    else ft.Colors.RED if severity == "High" else ft.Colors.GREEN
                )
            )

            self.history_list.controls.append(
                ft.ListTile(
                    leading=thumb_image,
                    title=ft.Column(
                        controls=[
                            ft.Text(filename, size=16, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                f"Severity: {severity} ({probability*100:.1f}%)",
                                size=14,
                            ),
                        ],
                        spacing=2,
                    ),
                    subtitle=ft.Text(
                        f"Uploaded on {date} at {time}", size=12, color=ft.Colors.GREY
                    ),
                    is_three_line=True,
                    bgcolor=ft.Colors.with_opacity(0.1, bgcolor),
                    shape=ft.RoundedRectangleBorder(radius=10),
                    on_click=lambda _, file=crack: show_full(self.page, file)
                )
            )

        self.history_body.content = self.history_list
        self.page.update()
