import flet as ft
import flet_video as ftv

from utils.file_utils import get_file_type
from views.template import TemplatePage
from services.crack_service import add_crack_service

class FullViewPage(TemplatePage):
    def __init__(self, page: ft.Page, url):
        super().__init__(page)
        self.file_url = url

        is_video = get_file_type(url) == "video" # Determine if the file is a video based on its URL or extension

        if is_video: # For videos, use the video player
            video_playlist = [ftv.VideoMedia(resource=self.file_url)]
            media_control = ft.Container(
                content=ftv.Video(
                    playlist=video_playlist,
                    title=self.file_url.rsplit('/', 1)[-1],
                    expand=True,
                    autoplay=True,
                ),
                expand=True,
            )

        else: # For images, use the interactive viewer
            media_control = ft.InteractiveViewer(
            ft.Container(
                content=ft.Image(
                    src=self.file_url,
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
            leading=self.cancel_btn,
            automatically_imply_leading=False,
            force_material_transparency=True,
        )

        self.body = ft.Column(
            controls=[self.full_view_content],
            expand=True,
        )

        return self.layout(
            route="/full_view",
            controls=[self.app_bar, self.body],
        )
    
