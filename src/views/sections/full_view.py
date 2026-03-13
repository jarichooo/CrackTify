import flet as ft
import flet_video as ftv

from utils.file_utils import get_file_type, cloudinary_to_download_url
from views.template import TemplatePage
from services.crack_service import add_crack_service


class FullViewPage(TemplatePage):
    def __init__(self, page: ft.Page, file: dict, on_close: callable=None):
        super().__init__(page)
        self.id = file.get("id")
        self.filename = file.get("filename")
        self.severity = file.get("severity")
        self.probability = file.get("probability")
        self.date_str = file.get("detected_at")
        self.file_url = file.get("file_url")

        self.on_close = on_close  # Callback to refresh home/gallery/history after closing full view

        is_video = (
            get_file_type(self.file_url) == "video"
        )  # Determine if the file is a video based on its URL or extension

        if is_video:  # For videos, use the video player
            video_playlist = [ftv.VideoMedia(resource=self.file_url)]
            media_control = ft.Container(
                content=ftv.Video(
                    playlist=video_playlist,
                    title=self.filename or "Unknown",
                    # expand=True,
                    autoplay=True,
                ),
                height=self.page.height - 200,  # leave space for app bar
            )

        else:  # For images, use the interactive viewer
            media_control = ft.InteractiveViewer(
                ft.Container(
                    content=ft.Image(
                        src=self.file_url,
                        fit=ft.BoxFit.CONTAIN,  # keep entire image visible
                    ),
                    width=2000,  # large canvas for zooming
                    height=2000,  # large canvas for zooming
                ),
                boundary_margin=ft.Margin.all(1000),  # extra panning space
                min_scale=0.5,  # zoom out limit
                max_scale=5.0,  # zoom in limit
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )

        # Full view content
        self.full_view_content = ft.Container(
            content=media_control,
            alignment=ft.Alignment.CENTER,
            height=self.page.height - 60,  # leave space for app bar
        )

        # Close button
        self.cancel_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Close Full View",
            on_click=lambda _: self.page.views.pop(),
        )

    def build(self) -> ft.View:
        """Builds the full view page view."""
        self.app_bar = ft.AppBar(
            title=ft.Text(self.filename or "Unknown"),
            leading=self.cancel_btn,
            automatically_imply_leading=False,
            force_material_transparency=True,
            actions=[
                # Additional actions can be added here if needed
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content="Download",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=self.download_file,
                        ),
                        ft.PopupMenuItem(
                            content="Delete",
                            icon=ft.Icons.DELETE,
                            on_click=lambda _: self.delete_image(self.id),
                        ),
                        ft.PopupMenuItem(
                            content="Properties",
                            icon=ft.Icons.INFO,
                            on_click=lambda _: self.display_properties(self.file_url),
                        ),
                    ]
                )
            ],
        )

        self.body = ft.Column(
            controls=[self.full_view_content],
            expand=True,
        )

        return self.layout(
            route="/full_view",
            controls=[self.app_bar, self.body],
        )

    def extract_time(self, date_str):
        if "T" in date_str:
            date = date_str.split("T")[0] if "T" in date_str else date_str
            time = date_str.split("T")[1].split(".")[0] if "T" in date_str else ""
            return date, time

        return date_str, ""

    async def download_file(self):
        """Opens browser to download the file using the file URL."""
        dl_url = cloudinary_to_download_url(self.file_url)
        await self.page.launch_url(dl_url)

    def delete_image(self, id):
        """Delete the image with the given ID and show a confirmation dialog."""

        confirm_dialog = ft.AlertDialog(
            title="Confirm Deletion",
            content=ft.Text(
                "Are you sure you want to delete this file? This action cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.pop_dialog()),
                ft.TextButton(
                    "Delete",
                    on_click=lambda e, id=id: self.page.run_task(
                        self.confirm_delete, e, id
                    ),
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED,  # Red color for delete action
                    ),
                ),
            ],
        )
        self.page.show_dialog(confirm_dialog)

    async def confirm_delete(self, e, cid):
        from services.crack_service import delete_crack_service
        self.show_loading("Deleting file...")

        res = await delete_crack_service(
            cid
        )  # Call the service to delete the crack file
        if not res.get("success"):

            error_dialog = ft.AlertDialog(
                title="Deletion Failed",
                content=ft.Text("Failed to delete the file. Please try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())
                ],
            )
            self.hide_loading()  # Hide the loading indicator before showing the error dialog
            self.page.show_dialog(error_dialog)
            return

        self.hide_loading()  # Hide the loading indicator
        self.page.pop_dialog()  # Close the confirmation dialog
        self.page.views.pop()  # Close the full view page to return to the gallery/history

        if self.on_close:
            self.on_close()  # Trigger the callback to refresh the home/gallery/history page

    def display_properties(self, url):
        date, time = self.extract_time(self.date_str)

        def prop_row(label, value):
            return ft.Row(
                controls=[
                    ft.Text(label, width=110),
                    ft.Text(":", width=10),
                    ft.Text(
                        value, overflow=ft.TextOverflow.FADE, max_lines=1, width=200
                    ),
                ],
                spacing=0,
            )

        info_dialog = ft.AlertDialog(
            title="Properties",
            content=ft.Column(
                controls=[
                    prop_row("Name", self.filename),
                    prop_row("Time", f"{date} at {time}"),
                    prop_row("Severity", str(self.severity)),
                    prop_row("Probability", f"{self.probability * 100:.1f}%"),
                ],
                height=120,
                spacing=10,
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.page.pop_dialog())],
        )

        self.page.show_dialog(info_dialog)
