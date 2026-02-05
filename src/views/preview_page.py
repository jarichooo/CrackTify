import asyncio
import os
import shutil
from pathlib import Path

import flet as ft
import flet_video as ftv
from .template import TemplatePage

class PreviewPage(TemplatePage):
    def __init__(self, page: ft.Page, file: ft.FilePickerFile, state):
        super().__init__(page)
        self.selected_file = file
        self.state = state

        # Determine file type
        ext = file.name.lower().rsplit('.', 1)[-1]

        if ext in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
            # Image fully covers screen and zoomable
            media_control = ft.InteractiveViewer(
            ft.Container(
                content=ft.Image(
                    src=file.path,
                    fit=ft.BoxFit.CONTAIN,  # keep entire image visible
                ),
                width=2000,  # large canvas for zooming
                height=2000, # large canvas for zooming
            ),
            boundary_margin=ft.Margin.all(1000),  # extra panning space
            min_scale=0.5,   # zoom out limit
            max_scale=5.0,   # zoom in limit
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
            on_click=self.upload_file,
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
    
    async def upload_file(self, e):
        """Uploads the selected file to the server."""
        if not self.selected_file:
            return
        
        await self.state.file_picker.upload(
            files=[
                ft.FilePickerUploadFile(
                    name=f.name,
                    upload_url=self.page.get_upload_url(
                        f"{f.name}", 60
                    )
                )
                for f in self.state.picked_file
            ]
        )

        # Show snackbar
        self.snack_bar = ft.SnackBar(
            ft.Text(f"{self.selected_file.name} uploaded successfully!"),
            bgcolor=ft.Colors.GREEN_500,
        )
        self.page.show_dialog(self.snack_bar)
        self.page.update()

        self.page.views.pop()  # Close preview page after upload

    # # TODO: FIX UPLOAD FOR ANDROID AND DESKTOP
    # async def upload_file(self, e):
    #     if not self.selected_file or not self.selected_file.path:
    #         return

    #     try:
    #         uploads_dir = os.path.join(os.getenv("EXTERNAL_STORAGE"), "Android", "data", "com.mycompany.cracktify", "files", "cracktify")

    #         src = Path(self.selected_file.path)
    #         dst = os.path.join(uploads_dir, src.name)

    #         shutil.copyfile(src, dst)

    #         self.page.snack_bar = ft.SnackBar(
    #             ft.Text(f"{src.name} uploaded successfully"),
    #             bgcolor=ft.Colors.GREEN_500,
    #         )
    #         self.page.snack_bar.open = True
    #         self.page.update()

    #         self.page.views.pop()

    #     except Exception as err:
    #         self.page.snack_bar = ft.SnackBar(
    #             ft.Text(f"UPLOAD ERROR: {err}"),
    #             bgcolor=ft.Colors.RED_500,
    #         )
    #         self.page.snack_bar.open = True
            # self.page.update()
