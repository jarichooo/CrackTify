import flet as ft
import base64
from typing import List
from pathlib import Path

from services.group_service import (
    fetch_user_groups,
    fetch_groups,
    create_group,
    join_group
)
from widgets.inputs import AppTextField
from utils.image_utils import image_to_base64


class GroupsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = self.page.client_storage.get("user_info")
        self.user_id = self.user.get("id") if self.user else None
        self.selected_avatar_path: str | None = None  # store path now

        # Cache to speed up repeated views
        self.cached_user_groups = []
        self.cached_joinable_groups = []


    # MAIN PAGE BUILD
    def build(self) -> List[ft.Control]:
        self.current_view = "my_groups"  # or "join_groups"

        # Action buttons
        self.create_group_button = ft.ElevatedButton(
            text="Create New Group",
            width=150,
            on_click=self.show_create_group_dialog
        )
        self.join_group_button = ft.ElevatedButton(
            text="Join Group",
            width=150,
            on_click=self.show_join_groups_view 
        )
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh Groups",
            on_click=lambda e: self.page.run_task(self.refresh_groups)
        )

        self.action_buttons = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Row(
                controls=[self.create_group_button, self.join_group_button, self.refresh_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            )
        )

        # Container where views will change
        self.content_container = ft.Column(spacing=5)

        # ListView for the page, **scrollable**
        self.list_view = ft.ListView(
            controls=[self.content_container],
            spacing=10,
            expand=True,           # allow to fill available space
        )

        # Load user groups initially
        self.page.run_task(self.load_user_groups)

        return [self.action_buttons, ft.Container(expand=True, content=self.list_view)]

    def filter_content(self, query: str):
        """ Filter groups based on search query """
        query_lower = query.lower()

        if self.current_view == "join_groups":
            # Filter joinable groups
            filtered_joinable_groups = [
                g for g in self.cached_joinable_groups.get("groups", [])
                if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
            ]
            self._render_joinable_groups({"groups": filtered_joinable_groups})
            return
     
        # Filter user groups
        filtered_user_groups = [
            g for g in self.cached_user_groups.get("groups", [])
            if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
        ]

        # Clear current content
        self.content_container.controls.clear()
        
        # Render filtered user groups
        for g in filtered_user_groups:
            members_count = len(g.get("members", []))
            last_activity = g["members"][-1]["joined_at"] if members_count > 0 else "N/A"

            tile = ft.Container(
                padding=15,
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                margin=ft.margin.only(bottom=10),
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
                content=ft.Column([
                    ft.Text(g["name"], size=18, weight="bold"),
                    ft.Row([
                        ft.Text(f"Members: {members_count}"),
                        # ft.Text(f"Last Activity: {last_activity}")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
            self.content_container.controls.append(tile)

        self.page.update()

    # REFRESH GROUPS
    async def refresh_groups(self):
        self.cached_user_groups = []
        self.cached_joinable_groups = []

        await self.load_user_groups()

    # LOAD USER GROUPS
    async def load_user_groups(self):
        self.current_view = "my_groups"
        try:
            if not self.cached_user_groups:
                self.cached_user_groups = await fetch_user_groups(self.user_id)

            self.content_container.controls.clear()

            for g in self.cached_user_groups.get("groups", []):
                members_count = len(g.get("members", []))
                last_activity = g["members"][-1]["joined_at"] if members_count > 0 else "N/A"

                tile = ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                    margin=ft.margin.only(bottom=10),
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
                    content=ft.Column([
                        ft.Text(g["name"], size=18, weight="bold"),
                        ft.Row([
                            ft.Text(f"Members: {members_count}"),
                            # ft.Text(f"Last Activity: {last_activity}")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
                self.content_container.controls.append(tile)

            self.page.update()
        except Exception as ex:
            print("Error loading user groups:", ex)

    # SHOW JOIN GROUPS VIEW
    def show_join_groups_view(self, e=None):
        self.current_view = "join_groups"
        self.content_container.controls.clear()

        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )
        self.content_container.controls.append(back_button)

        # Always reload joinable groups to get fresh data
        self.page.run_task(self.load_joinable_groups)

    # LOAD JOINABLE GROUPS
    async def load_joinable_groups(self):
        try:
            self.cached_joinable_groups = await fetch_groups(self.user_id)
            self._render_joinable_groups(self.cached_joinable_groups)
        except Exception as ex:
            print("Error loading joinable groups:", ex)

    # RENDER JOINABLE GROUPS
    def _render_joinable_groups(self, joinable_data):
        self.content_container.controls = self.content_container.controls[:1]  # keep only back button

        for g in joinable_data.get("groups", []):
            gid = g["id"]

            def make_join_fn(group_id):
                async def join_fn():
                    await self.join_group_action(group_id)
                return join_fn

            join_handler = make_join_fn(gid)

            card = ft.Container(
                padding=12,
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                margin=ft.margin.only(bottom=10),
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                content=ft.Row(
                    controls=[
                        ft.Text(g["name"], size=16),
                        ft.ElevatedButton(
                            "Join",
                            on_click=lambda e, f=join_handler: self.page.run_task(f)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            self.content_container.controls.append(card)

        self.page.update()

    # JOIN GROUP ACTION
    async def join_group_action(self, group_id):
        try:
            await join_group(self.user_id, group_id)
            self.cached_user_groups = []
            self.cached_joinable_groups = []
            self.page.run_task(self.load_user_groups)
        except Exception as ex:
            print("Error joining group:", ex)

    # CREATE GROUP DIALOG
    def show_create_group_dialog(self, e):
        file_picker = ft.FilePicker(on_result=self.on_avatar_picked)
        self.page.overlay.append(file_picker)

        # Upload box
        self.upload_box = ft.Container(
            width=125,
            height=125,
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=12,
            alignment=ft.alignment.center,
            content=ft.Icon(ft.Icons.UPLOAD_FILE, size=50),
            on_click=lambda e: file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["png", "jpg", "jpeg"]
            )
        )

        self.group_name_input = AppTextField(label="Group Name")
        self.group_description_input = AppTextField(label="Description", multiline=True, max_lines=3)

        self.dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=18),
            inset_padding=ft.padding.all(20),
            title=ft.Text("Create New Group", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=360,
                height=140,
                content=ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[self.upload_box, ft.Column([self.group_name_input, self.group_description_input], spacing=10, expand=True)]
                )
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dialog)),
                ft.TextButton("Create", on_click=lambda e: self.page.run_task(self.create_group_action))
            ]
        )
        self.page.open(self.dialog)

    # FILE PICK HANDLER
    def on_avatar_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        file = e.files[0]
        if not file.path:
            print("Mobile: File path not available!")
            return

        self.selected_avatar_path = file.path
        b64 = image_to_base64(file.path)  # use path now
        self.upload_box.content = ft.Image(
            src_base64=b64,
            width=125,
            height=125,
            fit=ft.ImageFit.COVER,
            border_radius=12
        )
        self.page.update()

    # CREATE GROUP ACTION
    async def create_group_action(self):
        name = self.group_name_input.value
        desc = self.group_description_input.value

        if not name:
            print("Group name required")
            return

        avatar_b64 = image_to_base64(self.selected_avatar_path) if self.selected_avatar_path else ""

        await create_group(name=name, description=desc, avatar_url=avatar_b64, admin_id=self.user_id)

        self.page.close(self.dialog)
        self.cached_user_groups = []
        self.page.run_task(self.load_user_groups)
