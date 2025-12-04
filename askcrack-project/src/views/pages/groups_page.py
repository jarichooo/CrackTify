import flet as ft
import base64
from typing import List

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

        # Load user data
        self.user = self.page.client_storage.get("user_info")
        self.user_id = self.user.get("id") if self.user else None

        # Store avatar bytes for create dialog
        self.selected_avatar_bytes = None

    # MAIN PAGE BUILD
    def build(self) -> List[ft.Control]:

        # Buttons at the top
        self.create_group_button = ft.ElevatedButton(
            text="Create New Group",
            width=160,
            on_click=self.show_create_group_dialog
        )

        self.join_group_button = ft.ElevatedButton(
            text="Join Group",
            width=160,
            on_click=self.show_join_groups_view
        )

        self.action_buttons = ft.Container(
            ft.Row(
                controls=[self.create_group_button, self.join_group_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        )

        # Container where views will change
        self.content_container = ft.Column(spacing=10)

        # Whole page ListView
        self.list_view = ft.ListView(
            controls=[self.content_container],
            spacing=15
        )

        # Load user's groups
        self.page.run_task(self.load_user_groups)

        return [self.action_buttons, self.list_view]

    # LOAD USER GROUPS VIEW
    async def load_user_groups(self, e=None):
        self.content_container.controls.clear()

        groups_data = await fetch_user_groups(self.user_id)

        for g in groups_data.get("groups", []):
            members_count = len(g.get("members", []))
            last_activity = (
                g["members"][-1]["joined_at"] if members_count > 0 else "N/A"
            )

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
                        ft.Text(f"Last Activity: {last_activity}")
                    ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ])
            )
            self.content_container.controls.append(tile)

        self.page.update()

    # SHOW JOIN GROUPS VIEW
    def show_join_groups_view(self, e=None):
        self.content_container.controls.clear()

        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )

        self.content_container.controls.append(back_button)

        # Load joinable groups
        self.page.run_task(self.load_joinable_groups)

    async def load_joinable_groups(self, e=None):
        joinable_data = await fetch_groups()

        for g in joinable_data.get("groups", []):
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
                            on_click=lambda e, gid=g["id"]: 
                                self.page.run_task(self.join_group_action(gid))
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            self.content_container.controls.append(card)

        self.page.update()

    async def join_group_action(self, group_id):
        await join_group(self.user_id, group_id)
        # Reload user groups after join
        self.page.run_task(self.load_user_groups)

    # CREATE GROUP DIALOG
    def show_create_group_dialog(self, e):

        # FIX for mobile bug — FilePicker without id
        file_picker = ft.FilePicker(
            on_result=self.on_avatar_picked
        )
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
                allowed_extensions=["png", "jpg", "jpeg"],
            ),
        )

        self.group_name_input = AppTextField(label="Group Name")
        self.group_description_input = AppTextField(
            label="Description",
            multiline=True,
            max_lines=3
        )

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
                    controls=[
                        self.upload_box,
                        ft.Column([
                            self.group_name_input,
                            self.group_description_input
                        ], spacing=10, expand=True)
                    ]
                )
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dialog)),
                ft.TextButton("Create", on_click=lambda e: self.page.run_task(self.create_group_action))
            ]
        )

        self.page.open(self.dialog)

    # FILE PICK HANDLER — MOBILE SAFE
    def on_avatar_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file = e.files[0]

        if not file.bytes:
            print("Mobile: File bytes not available!")
            return

        self.selected_avatar_bytes = file.bytes

        b64 = image_to_base64(file.bytes)

        self.upload_box.content = ft.Image(
            src=f"data:image/png;base64,{b64}",
            width=125,
            height=125,
            fit=ft.ImageFit.COVER,
            border_radius=12
        )
        self.page.update()

    # CREATE GROUP ACTION
    async def create_group_action(self, e=None):
        name = self.group_name_input.value
        desc = self.group_description_input.value

        if not name:
            print("Group name required")
            return

        avatar_b64 = (
            base64.b64encode(self.selected_avatar_bytes).decode()
            if self.selected_avatar_bytes else ""
        )

        await create_group(
            name=name,
            description=desc,
            avatar_url=avatar_b64,
            admin_id=self.user_id
        )

        # Close dialog
        self.page.close(self.dialog)

        # Reload groups
        self.content_container.controls.clear()
        self.page.run_task(self.load_user_groups)
