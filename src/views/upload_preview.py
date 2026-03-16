import asyncio
import os
import shutil
from pathlib import Path

import flet as ft
import flet_video as ftv
from .template import TemplatePage


class PreviewPage(TemplatePage):
    def __init__(
        self,
        page: ft.Page,
        file: ft.FilePickerFile,
        state,
        user,
        on_close: callable = None,
    ):
        super().__init__(page)
        self.selected_file = file
        self.state = state
        self.user = user
        self.on_close = on_close

        self.upload_task: asyncio.Task | None = None
        self.is_uploading = False

        # Determine file type
        ext = file.name.lower().rsplit(".", 1)[-1]

        if ext in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
            # Image fully covers screen and zoomable
            media_control = ft.InteractiveViewer(
                ft.Container(
                    content=ft.Image(
                        src=file.path,
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

        elif ext in ["mp4", "mov", "webm", "avi", "mkv"]:
            # Video wrapped in container for full screen
            video_playlist = [ftv.VideoMedia(resource=file.path)]
            media_control = ft.Container(
                content=ftv.Video(
                    playlist=video_playlist,
                    title=file.name,
                    expand=True,
                    autoplay=True,
                ),
                expand=True,
            )
        else:
            # Other files: just show filename
            media_control = ft.Text(file.name, size=20)

        # Preview content
        self.preview_content = ft.Container(
            content=media_control,
            alignment=ft.Alignment.CENTER,
            height=self.page.height - 200,
        )

        # Upload button at bottom-right
        self.upload_btn = ft.FloatingActionButton(
            content="Upload",
            icon=ft.Icons.CLOUD_UPLOAD,
            tooltip="Upload",
            on_click=self.handle_upload_file,
        )

        # Close button
        self.close_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Close Preview",
            on_click=lambda _: self.page.views.pop(),
        )

    def build(self) -> ft.View:
        """Builds the preview page view."""
        self.app_bar = ft.AppBar(
            leading=self.close_btn,
            title=ft.Text("Preview"),
            automatically_imply_leading=False,
        )

        self.body = ft.Column(
            controls=[self.preview_content],
            expand=True,
        )

        return self.layout(
            route="/preview",
            controls=[self.app_bar, self.body],
            floating_action_button=self.upload_btn,
        )

    async def handle_upload_file(self, e):
        """Handles the upload button click, managing both upload and cancel states."""
        # CANCEL MODE
        if self.is_uploading and self.upload_task:
            self.upload_task.cancel()
            self.reset_upload_button()
            return

        # UPLOAD MODE
        self.is_uploading = True
        self.upload_btn.disabled = True
        self.upload_btn.bgcolor = ft.Colors.with_opacity(
            0.5, ft.Colors.GREY_500
        )  # indicate processing
        self.page.update()

        self.upload_task = asyncio.create_task(self._upload_flow())

    def show_cancel_button(self):
        """Updates the upload button to a cancel button during retries."""
        self.upload_btn.disabled = False
        self.upload_btn.icon = ft.Icons.CANCEL
        self.upload_btn.content = "Cancel"
        self.upload_btn.tooltip = "Cancel Upload"
        self.upload_btn.bgcolor = ft.Colors.RED_500
        self.page.update()

    def reset_upload_button(self):
        """Resets the upload button to its original state."""
        self.is_uploading = False
        self.upload_task = None

        self.upload_btn.icon = ft.Icons.CLOUD_UPLOAD
        self.upload_btn.content = "Upload"
        self.upload_btn.tooltip = "Upload"
        self.upload_btn.bgcolor = None
        self.upload_btn.disabled = False
        self.page.update()

    async def _upload_flow(self):
        """Handles the upload process with retries and cancellation."""
        from services.file_service import upload_file
        from services.crack_service import detect_crack, add_crack_service

        MAX_RETRIES = 5
        detect_resp = None

        try:
            # Upload ONCE
            self.show_loading("Uploading file...")
            upload_result = await upload_file(self.selected_file.path)

            for attempt in range(1, MAX_RETRIES + 1):

                # Show cancel button on retry
                if attempt >= 2:
                    self.show_cancel_button()

                try:
                    # Detect (retry if needed)
                    if not detect_resp:
                        self.show_loading(f"Detecting cracks...")
                        detect_resp = await detect_crack(
                            upload_result, confidence_threshold=0.5, timeout=60
                        )

                        if not detect_resp or not detect_resp.get("success", True):
                            detect_resp = None
                            raise RuntimeError("Detection failed")

                    # Save (retryable)
                    crack_data = {
                        "user_id": self.user["id"],
                        "file_url": detect_resp["file_url"],
                        "filename": os.path.splitext(self.selected_file.name)[0],
                        "severity": detect_resp.get("severity", "unknown"),
                        "probability": detect_resp.get("probability", 0),
                    }

                    self.show_loading(f"Saving results...")
                    await add_crack_service(self.user["id"], crack_data)

                    # SUCCESS
                    self.page.show_dialog(
                        ft.SnackBar(
                            ft.Text("Uploaded and analyzed successfully!"),
                            bgcolor=ft.Colors.GREEN_500,
                        )
                    )

                    if self.on_close:
                        self.on_close()

                    self.page.views.pop()
                    return

                except Exception as err:
                    if attempt == MAX_RETRIES:
                        raise
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            self.page.show_dialog(
                ft.SnackBar(
                    ft.Text("Upload cancelled"),
                    bgcolor=ft.Colors.ORANGE_500,
                )
            )

        except Exception as err:
            self.page.show_dialog(
                ft.SnackBar(
                    ft.Text(f"Process failed: {err}"),
                    bgcolor=ft.Colors.RED_500,
                )
            )

        finally:
            self.hide_loading()
            self.reset_upload_button()
