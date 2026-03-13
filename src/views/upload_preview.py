import asyncio
import os
import shutil
from pathlib import Path

import flet as ft
import flet_video as ftv
from .template import TemplatePage


class PreviewPage(TemplatePage):
    def __init__(self, page: ft.Page, file: ft.FilePickerFile, state, user):
        super().__init__(page)
        self.selected_file = file
        self.state = state
        self.user = user

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
        self.cancel_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Close Preview",
            on_click=lambda _: self.page.views.pop(),
        )

    def build(self) -> ft.View:
        """Builds the preview page view."""
        self.app_bar = ft.AppBar(
            leading=self.cancel_btn,
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
        """Handles the upload button click event (sequential & cancellation-safe)."""
        from services.file_service import upload_file
        from services.crack_service import detect_crack, add_crack_service

        if not self.selected_file:
            return

        self.hide_loading()  # Ensure no loading from previous attempts
        self.upload_btn.disabled = True
        self.upload_btn.bgcolor = ft.Colors.GRAY_400
        self.page.update()

        try:
            # STEP 1: UPLOAD (MUST FINISH)
            self.show_loading("Uploading file...")
            upload_result = await upload_file(self.selected_file.path)

            if not upload_result:
                raise RuntimeError("Upload failed: no response")

            # STEP 2: DETECT (MUST FINISH)
            self.show_loading("Detecting cracks...")
            detect_resp = await detect_crack(upload_result, confidence_threshold=0.5)

            if not detect_resp or not detect_resp.get("success", True):
                raise RuntimeError(
                    detect_resp.get("message", "Crack detection failed")
                    if detect_resp else "Crack detection returned no response"
                )

            # STEP 3: SAVE TO DB (MUST FINISH)
            user_id = self.user.get("id")
            if not user_id:
                raise RuntimeError("User not authenticated")

            crack_data = {
                "user_id": user_id,
                "file_url": detect_resp["file_url"],
                "filename": os.path.splitext(self.selected_file.name)[0],
                "severity": detect_resp.get("severity", "unknown"),
                "probability": detect_resp.get("probability", 0),
            }

            await add_crack_service(user_id, crack_data)

            # SUCCESS UI
            self.page.show_dialog(
                ft.SnackBar(
                    ft.Text("Uploaded and analyzed successfully!"),
                    bgcolor=ft.Colors.GREEN_500,
                )
            )

            # Navigation ONLY after everything succeeded
            self.page.views.pop()

        except asyncio.CancelledError:
            # Do NOT swallow cancellations
            print("Upload task cancelled")
            raise

        except Exception as err:
            self.page.show_dialog(
                ft.SnackBar(
                    ft.Text(f"Process failed: {err}"),
                    bgcolor=ft.Colors.RED_500,
                )
            )

        finally:
            self.hide_loading()
            self.upload_btn.disabled = False
            self.upload_btn.bgcolor = None
            self.page.update()
