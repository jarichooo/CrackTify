import flet as ft
import flet_video as ftv

from utils.file_utils import get_file_type, cloudinary_to_download_url
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
        self.page.run_task(self.run_permission_check)  # Check if user has edit access to this crack

        self.app_bar = ft.AppBar(
            title=ft.Text(self.filename or "Unknown"),
            leading=self.cancel_btn,
            automatically_imply_leading=False,
            force_material_transparency=True,
            actions=[
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
            icon=ft.Icons.INFO_OUTLINED,  # Default; updated after permission check
            on_click=lambda _: self.page.show_dialog(self.bottom_sheet),
        )

        self.save_remark_btn = PrimaryButton(
            "Save", icon=ft.Icons.SAVE, on_click=self.save_remark_changes, expand=True
        )

        self.remark_field = TextField(
            label="Remark",
            multiline=True,
            value=self.remark,
            hint_text="No remark provided.",
            width=400,
            read_only=True,  # Always start read-only; updated after permission check
        )

        self.severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[
                ft.dropdown.Option(key="Low", text="Low"),
                ft.dropdown.Option(key="Mild", text="Mild"),
                ft.dropdown.Option(key="High", text="High"),
            ],
            value=self.severity,
            expand=1,
            visible=False,  # Hidden until permission check confirms edit access
        )

        self.probability_field = TextField(
            label="Probability",
            hint_text="Enter probability (0-1)",
            value=str(self.probability),
            expand=1,
            visible=False,  # Hidden until permission check confirms edit access
        )

        # Section header for severity/probability editing — stored as ref so we can toggle it
        self.edit_section_header = ft.Text(
            "Edit Severity and Probability",
            size=20,
            visible=False,  # Hidden until permission check confirms edit access
        )

        # Row wrapping the save button — stored as ref so we can toggle visibility
        self.save_remark_row = ft.Row(
            controls=[self.save_remark_btn],
            visible=False,  # Hidden until permission check confirms edit access
        )

        self.bottom_sheet = ft.BottomSheet(
            draggable=True,
            show_drag_handle=True,
            content=ft.Container(
                content=ft.Column(
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Remark", size=20),
                        self.remark_field,
                        self.edit_section_header,
                        ft.Row(
                            spacing=10,
                            controls=[
                                self.severity_dropdown,
                                self.probability_field,
                            ],
                        ),
                        self.save_remark_row,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=20,
                expand=True,
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
            self.hide_loading()
            self.page.show_dialog(error_dialog)
            return

        self.filename = new_name
        self.app_bar.title = ft.Text(self.filename)
        self.hide_loading()
        self.page.update()

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
                        color=ft.Colors.RED,
                    ),
                ),
            ],
        )
        self.page.show_dialog(confirm_dialog)

    async def confirm_delete(self, e, cid):
        from services.crack_service import delete_crack_service

        self.page.pop_dialog()
        self.show_loading("Deleting file...")
        self.page.update()

        res = await delete_crack_service(cid)
        if not res.get("success"):
            error_dialog = ft.AlertDialog(
                title="Deletion Failed",
                content=ft.Text("Failed to delete the file. Please try again."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())
                ],
            )
            self.hide_loading()
            self.page.show_dialog(error_dialog)
            return

        self.hide_loading()
        self.page.views.pop()

        if self.on_close:
            self.on_close()

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
        """
        Calls the server to determine if the current user can edit this crack.

        - Engineers with access: remark becomes editable + severity/probability
          edit fields and save button are shown.
        - Owners (civilians) without edit access: remark is read-only, edit
          fields and save button stay hidden.
        """
        from services.crack_service import can_edit_crack

        # FIX: arguments were previously swapped — service expects (crack_id, user_id)
        resp = await can_edit_crack(self.id, self.user.get("id"))
        self.has_edit_access = resp.get("can_edit", False)

        # Update FAB icon to signal edit vs info-only mode
        self.edit_properties_fab.icon = (
            ft.Icons.EDIT if self.has_edit_access else ft.Icons.INFO_OUTLINED
        )

        # Remark: editable for engineers, read-only for owners
        self.remark_field.read_only = not self.has_edit_access

        # Severity / probability fields + section header: visible only to editors
        self.edit_section_header.visible = self.has_edit_access
        self.severity_dropdown.visible = self.has_edit_access
        self.probability_field.visible = self.has_edit_access

        # FIX: update the Row wrapper, not the button inside it
        self.save_remark_row.visible = self.has_edit_access

        try:
            self.edit_properties_fab.update()
            self.bottom_sheet.update()
        except Exception:
            pass  # Bottom sheet may not be mounted yet — changes will reflect on open

    async def save_remark_changes(self, e):
        """Saves the changes made to the crack's remark, severity, and probability."""
        from services.crack_service import update_crack_service

        new_remark = self.remark_field.value
        new_severity = self.severity_dropdown.value
        new_probability = self.probability_field.value

        if not new_probability:
            error_dialog = ft.AlertDialog(
                title="Invalid Input",
                content=ft.Text(
                    "Probability cannot be empty. Please enter a value between 0 and 1."
                ),
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
            self.hide_loading()
            self.page.show_dialog(error_dialog)
            return

        # Sync local state with saved values
        self.remark = new_remark
        self.severity = new_severity
        self.probability = float(new_probability)
        self.hide_loading()
        self.page.pop_dialog()  # Close the bottom sheet after saving