import flet as ft
import flet_video as ftv

from utils.file_utils import get_file_type, cloudinary_to_download_url
from services.crack_service import can_edit_crack
from views.template import TemplatePage

from model.user import User

from widgets.inputs import TextField
from widgets.buttons import PrimaryButton


class FullViewPage(TemplatePage):
    def __init__(self, page: ft.Page, file: dict, on_close: callable = None):
        super().__init__(page)
        self.id = file.get("id")
        self.filename = file.get("filename")
        self.severity = file.get("severity")
        self.probability = file.get("probability")
        self.remark = file.get("remark", "")
        self.date_str = file.get("detected_at")
        self.file_url = file.get("file_url")

        self.user = User.to_dict()  # Get user data as a dictionary

        self.has_edit_access = False  # Will be set after checking permissions

        self.on_close = (
            on_close  # Callback to refresh home/gallery/history after closing full view
        )

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

        def close_full_view(e):
            self.page.views.pop()  # Close the full view page
            if self.on_close:
                self.on_close()  # Trigger the callback to refresh the home/gallery/history page

        # Close button
        self.cancel_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Close Full View",
            on_click=close_full_view,
        )

    def build(self) -> ft.View:
        """Builds the full view page view."""
        self.page.run_task(
            self.run_permission_check
        )  # Check if user has edit access to this crack

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
                            content="Rename",
                            icon=ft.Icons.EDIT,
                            on_click=self.rename_file,
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

        self.edit_properties_fab = ft.FloatingActionButton(
            icon=ft.Icons.INFO_OUTLINED if not self.has_edit_access else ft.Icons.EDIT,
            on_click=lambda _: self.page.show_dialog(self.bottom_sheet),
        )

        self.save_remark = PrimaryButton("Save", icon=ft.Icons.SAVE, on_click=self.save_remark_changes, expand=True)

        self.remark_field = TextField(
            label="Remark",
            multiline=True,
            value=self.remark,
            hint_text="No remark provided.",
            width=400,
            read_only=not self.has_edit_access,  # Make read-only if user doesn't have edit access
        )

        self.severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[
                ft.dropdown.Option(key="Low", text="Low"),
                ft.dropdown.Option(key="Medium", text="Medium"),
                ft.dropdown.Option(key="High", text="High"),
            ],
            value=self.severity,
            expand=1,
            visible=self.has_edit_access,  # Disable if user doesn't have edit access
        )
        self.probability_field = TextField(
            label="Probability",
            hint_text="Enter probability (0-1)",
            value=str(self.probability),
            expand=1,
            visible=self.has_edit_access,  # Make read-only if user doesn't have edit access
        )

        self.bottom_sheet = ft.BottomSheet(
            draggable=True,
            show_drag_handle=True,
            content=ft.Container(
                content=ft.Column(
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,  # ← makes Column scrollable
                    controls=[
                        ft.Text("Remark", size=20),
                        self.remark_field,
                        ft.Text("Edit Severity and Probability", size=20, visible=self.has_edit_access),  # Show section header only if user has edit access
                        ft.Row(
                            spacing=10,
                            controls=[
                                self.severity_dropdown,
                                self.probability_field,
                            ]
                        ),
                        ft.Row(self.save_remark, visible=self.has_edit_access),  # Show save button only if user has edit access
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=20,
                expand=True,  # ← let container fill available space
            ),
        )

        self.body = ft.Column(
            controls=[self.full_view_content],
            expand=True,
        )

        return self.layout(
            route="/full_view",
            floating_action_button=self.edit_properties_fab,
            controls=[self.app_bar, self.body],
        )

    def rename_file(self, e):
        """Placeholder for rename functionality."""
        self.rename_tf = ft.TextField(
            label="Filename",
            value=self.filename,
            width=300,
            autofocus=True,
            selection=(ft.TextSelection(0, len(self.filename))),
        )
        rename_dialog = ft.AlertDialog(
            title="Rename File",
            modal=True,
            content=self.rename_tf,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.pop_dialog()),
                ft.TextButton(
                    "Rename",
                    on_click=lambda e: self.page.run_task(
                        self.do_rename_file, self.rename_tf.value
                    ),
                ),
            ],
        )
        self.page.show_dialog(rename_dialog)

    async def do_rename_file(self, new_name):
        """Renames the file with the given new name."""
        from services.crack_service import update_crack_service

        self.page.pop_dialog()  # Close the rename dialog
        self.show_loading("Renaming file...")
        self.page.update()

        resp = await update_crack_service(self.id, {"filename": new_name})

        if not resp.get("success"):
            error_dialog = ft.AlertDialog(
                title="Rename Failed",
                content=ft.Text("Failed to rename the file. Please try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())
                ],
            )
            self.hide_loading()  # Hide the loading indicator before showing the error dialog
            self.page.show_dialog(error_dialog)
            return

        self.filename = new_name  # Update the filename in the UI
        self.app_bar.title = ft.Text(self.filename)  # Update the app bar title
        self.hide_loading()  # Hide the loading indicator
        self.page.update()  # Refresh the page to show the new filename

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

        self.page.pop_dialog()  # Close the confirmation dialog
        self.show_loading("Deleting file...")
        self.page.update()

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

    async def run_permission_check(self):
        """Checks if the current user has permission to edit this crack's remark."""
        from services.crack_service import can_edit_crack

        resp = await can_edit_crack(self.user.get("id"), self.id)

        self.has_edit_access = resp.get("can_edit", False)

    async def save_remark_changes(self, e):
        """Saves the changes made to the crack's remark and severity."""
        from services.crack_service import update_crack_service

        new_remark = self.remark_field.value
        new_severity = self.severity_dropdown.value
        new_probability = self.probability_field.value


        if not new_probability:
            error_dialog = ft.AlertDialog(
                title="Invalid Input",
                content=ft.Text("Probability cannot be empty. Please enter a value between 0 and 1."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())],
            )
            self.page.show_dialog(error_dialog)
            return

        self.show_loading("Saving changes...")
        self.page.update()

        resp = await update_crack_service(
            self.id,
            {
                "remark": new_remark,
                "severity": new_severity,
                "probability": float(new_probability),
            },
        )

        if not resp.get("success"):
            error_dialog = ft.AlertDialog(
                title="Update Failed",
                content=ft.Text("Failed to update the crack. Please try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())
                ],
            )
            self.hide_loading()  # Hide the loading indicator before showing the error dialog
            self.page.show_dialog(error_dialog)
            return

        self.remark = new_remark  # Update the remark in the UI
        self.severity = new_severity  # Update the severity in the UI
        self.probability = float(new_probability)  # Update the probability in the UI
        self.hide_loading()  # Hide the loading indicator
        self.page.pop_dialog()  # Close the bottom sheet after saving changes
