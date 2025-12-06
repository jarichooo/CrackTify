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

    def build(self) -> List[ft.Control]:
        """ Build the Groups Page UI """
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

    async def refresh_groups(self):
        """ Refresh both user groups and joinable groups """
        self.cached_user_groups = []
        self.cached_joinable_groups = []

        await self.load_user_groups()

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
        self.create_group_tile(filtered_user_groups)

        self.page.update()

    def _render_user_groups_list(self, groups_data):
        """ Render the list of user groups """
        if not groups_data: # if empty
            self.content_container.controls.append(
                ft.Column(
                    [ft.Text("No groups yet. Create or join one!", size=16, color=ft.Colors.GREY)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            )
            self.page.update()
            return

        for g in groups_data: # loop through groups
            members_count = len(g.get("members", []))
            critical_count = g.get("critical_cracks", 0)

            # Create ListTile for each user group
            tile = ft.ListTile(
                title=ft.Text(g["name"], size=18, weight="bold"),
                subtitle=ft.Row(
                    controls=[
                        ft.Text(f"👥 Members: {members_count}"),
                        ft.Container(width=10),
                        ft.Text(f"⚠ {critical_count} Critical", color=ft.Colors.RED) if critical_count > 0 else ft.Container()
                    ]
                ),
                trailing=ft.ElevatedButton(
                    "View",
                    width=80,
                    on_click=lambda e, gid=g["id"]: self.view_group(gid)
            ),
                content_padding=ft.padding.symmetric(vertical=10, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            )

            self.content_container.controls.append(tile)

        self.page.update()

    def _render_joinable_groups_list(self, joinable_data):
        """ Render the list of joinable groups """
        self.content_container.controls = self.content_container.controls[:1]  # keep back button

        for g in joinable_data.get("groups", []): # loop through groups
            gid = g["id"]

            def make_join_fn(group_id): # closure to capture group_id
                async def join_fn():
                    await self.join_group_action(group_id)
                return join_fn

            join_handler = make_join_fn(gid) # create join handler
            members_count = len(g.get("members", [])) # count members

            # Create ListTile for each joinable group
            tile = ft.ListTile(
                title=ft.Text(g["name"], size=18, weight="bold"),
                subtitle=ft.Text(f"👥 Members: {members_count}"),
                trailing=ft.ElevatedButton(
                    "Join",
                    width=80,
                    on_click=lambda e, f=join_handler: self.page.run_task(f)
                ),
                content_padding=ft.padding.symmetric(vertical=10, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            )

            self.content_container.controls.append(tile)

        self.page.update()

    async def load_user_groups(self):
        """ Load and display user's groups """
        self.current_view = "my_groups"
        try:
            if not self.cached_user_groups:
                self.cached_user_groups = await fetch_user_groups(self.user_id)

            self.content_container.controls.clear()


            self.content_container.controls.append(ft.TextButton("My Groups"))

            self._render_user_groups_list(self.cached_user_groups.get("groups", []))

            self.page.update()
        except Exception as ex:
            print("Error loading user groups:", ex)

    def show_join_groups_view(self, e=None):
        """ Switch to joinable groups view """
        self.current_view = "join_groups"
        self.content_container.controls.clear()

        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )
        self.content_container.controls.append(back_button)

        # Always reload joinable groups to get fresh data
        self.page.run_task(self.load_joinable_groups)

    async def load_joinable_groups(self):
        """ Load and display joinable groups """
        try:
            self.cached_joinable_groups = await fetch_groups(self.user_id)
            self._render_joinable_groups_list(self.cached_joinable_groups)

        except Exception as ex:
            print("Error loading joinable groups:", ex)

    async def join_group_action(self, group_id):
        try:
            await join_group(self.user_id, group_id)
            self.cached_user_groups = []
            self.cached_joinable_groups = []
            self.page.run_task(self.load_user_groups)
        except Exception as ex:
            print("Error joining group:", ex)

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
 
    async def create_group_action(self):
        """" Create a new group with provided details """
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

    def view_group(self, group_id):
        """ Navigate to the group detail page """
        # self.page.client_storage.set("current_group_id", group_id)
        # self.page.go("/group_detail")
        print(f"View group {group_id} - navigation not implemented yet")