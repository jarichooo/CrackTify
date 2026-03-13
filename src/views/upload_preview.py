import asyncio
import os
import shutil
from pathlib import Path

import flet as ft
import flet_video as ftv
from .template import TemplatePage


class PreviewPage(TemplatePage):
    def __init__(self, page: ft.Page, file: ft.FilePickerFile, state, user, on_close: callable=None):
        super().__init__(page)
        self.selected_file = file
        self.state = state
        self.user = user
        self.on_close = on_close

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
        """Handles the upload button click event with automatic retry on failure."""
        do_cancel = False  # Set to True if you want to show a cancel button during upload

        if do_cancel: # Cancel button logic
            self.hide_loading()  # Ensure no loading from previous attempts
            self.page.views.pop()
            return

        from services.file_service import upload_file
        from services.crack_service import detect_crack, add_crack_service

        if not self.selected_file:
            return

        self.hide_loading()  # Ensure no loading from previous attempts
        self.upload_btn.disabled = True
        self.upload_btn.bgcolor = ft.Colors.with_opacity(ft.Colors.GRAY_500, 0.5)
        self.page.update()

        # STEP 1: UPLOAD
        self.show_loading("Uploading file...")
        upload_result = await upload_file(self.selected_file.path)

        if not upload_result:
            raise RuntimeError("Upload failed: no response")

        MAX_RETRIES = 5
        attempt = 0
        success = False

        while attempt < MAX_RETRIES and not success:
            attempt += 1
            try:
                # STEP 2: DETECT
                self.show_loading(f"Detecting cracks... (Attempt {attempt})")
                detect_resp = await detect_crack(
                    upload_result, confidence_threshold=0.5
                )

                if not detect_resp or not detect_resp.get("success", True):
                    raise RuntimeError(
                        detect_resp.get("message", "Crack detection failed")
                        if detect_resp
                        else "Crack detection returned no response"
                    )

                # STEP 3: SAVE TO DB
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

                self.show_loading(f"Saving results... (Attempt {attempt})")
                await add_crack_service(user_id, crack_data)

                # SUCCESS UI
                self.page.show_dialog(
                    ft.SnackBar(
                        ft.Text("Uploaded and analyzed successfully!"),
                        bgcolor=ft.Colors.GREEN_500,
                    )
                )

                # Navigation ONLY after everything succeeded
                success = True
                self.page.views.pop()

                if self.on_close:
                    self.on_close()  # Trigger the callback to refresh the home/gallery/history page

            except asyncio.CancelledError:
                print("Upload task cancelled")
                raise

            except Exception as err:
                print(f"Attempt {attempt} failed: {err}")
                if attempt >= MAX_RETRIES:
                    self.page.show_dialog(
                        ft.SnackBar(
                            ft.Text(
                                f"Process failed after {MAX_RETRIES} attempts: {err}"
                            ),
                            bgcolor=ft.Colors.RED_500,
                        )
                    )
                else:
                    # Optional: wait a bit before retrying
                    await asyncio.sleep(1)

            finally:
                self.hide_loading()
                do_cancel = True  # Show cancel button after first attempt if desired
                self.upload_btn.icon = ft.Icons.CANCEL
                self.upload_btn.content = "Cancel"
                self.upload_btn.tooltip = "Cancel Upload"
                self.upload_btn.disabled = False
                self.upload_btn.bgcolor = ft.Colors.RED_500
                self.page.update()
