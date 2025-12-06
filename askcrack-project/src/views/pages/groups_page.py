import flet as ft
import base64
from typing import List
from pathlib import Path

from services.group_service import (
    fetch_user_groups,
    fetch_groups,
    fetch_group_info,
    create_group,
    join_group,
    edit_member,
    remove_member
)
from widgets.inputs import AppTextField
from utils.image_utils import image_to_base64


class GroupsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = self.page.client_storage.get("user_info")
        self.user_id = self.user.get("id") if self.user else None
        self.selected_avatar_path: str | None = None

        # Cache
        self.cached_user_groups = []
        self.cached_joinable_groups = []

        self.current_group_id: int | None = None

    def build(self) -> List[ft.Control]:
        """Build the Groups Page UI"""
        self.current_view = "my_groups"

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

        # Navigation bar (hidden initially)
        self.group_navbar = ft.NavigationBar(
            bgcolor=ft.Colors.TRANSPARENT,
            visible=False,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.GROUP, label="Members"),
                ft.NavigationBarDestination(icon=ft.Icons.IMAGE, label="Images"),
            ],
            on_change=self._on_group_nav_change,
        )

        # Container for changing views
        self.content_container = ft.Column(spacing=5)

        # Scrollable ListView
        self.list_view = ft.ListView(
            controls=[self.content_container],
            spacing=10,
            expand=True,
        )

        # Load user groups
        self.page.run_task(self.load_user_groups)

        return [
            self.action_buttons,
            ft.Container(expand=True, content=self.list_view),
            self.group_navbar 
        ]

    async def refresh_groups(self):
        self.cached_user_groups = []
        self.cached_joinable_groups = []
        await self.load_user_groups()

    def filter_content(self, query: str):
        query_lower = query.lower()
        if self.current_view == "join_groups":
            filtered_joinable = [
                g for g in self.cached_joinable_groups.get("groups", [])
                if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
            ]
            self._render_joinable_groups_list({"groups": filtered_joinable})
            return
     
        filtered_user = [
            g for g in self.cached_user_groups.get("groups", [])
            if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
        ]
        self.content_container.controls.clear()
        self._render_user_groups_list(filtered_user)
        self.page.update()

    def _render_user_groups_list(self, groups_data):
        if not groups_data:
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

        for g in groups_data:
            members_count = len(g.get("members", []))
            critical_count = g.get("critical_cracks", 0)

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
                    on_click=lambda e, gid=g["id"]: self.view_group_detail(gid)
                ),
                content_padding=ft.padding.symmetric(vertical=10, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            )

            self.content_container.controls.append(tile)
        self.page.update()

    def view_group_detail(self, group_id):
        self.current_group_id = group_id
        self.page.run_task(self.view_group)

    def _render_joinable_groups_list(self, joinable_data):
        self.content_container.controls.clear()
        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )
        self.content_container.controls.append(back_button)

        for g in joinable_data.get("groups", []):
            gid = g["id"]

            async def join_fn(group_id=gid):
                await self.join_group_action(group_id)

            members_count = len(g.get("members", []))

            tile = ft.ListTile(
                title=ft.Text(g["name"], size=18, weight="bold"),
                subtitle=ft.Text(f"👥 Members: {members_count}"),
                trailing=ft.ElevatedButton(
                    "Join",
                    width=80,
                    on_click=lambda e, f=join_fn: self.page.run_task(f)
                ),
                content_padding=ft.padding.symmetric(vertical=10, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            )

            self.content_container.controls.append(tile)

        self.page.update()

    async def load_user_groups(self):
        """Load and display the user's groups"""
        self.current_view = "my_groups"
        try:
            if not self.cached_user_groups:
                self.cached_user_groups = await fetch_user_groups(self.user_id) # Fetch group detail from API

            self.content_container.controls.clear()
            self.content_container.controls.append(ft.TextButton("My Groups"))  # Placeholder for title 
            self._render_user_groups_list(self.cached_user_groups.get("groups", []))
            self.page.update()
        except Exception as ex:
            print("Error loading user groups:", ex)

    def show_join_groups_view(self, e=None):
        """Show the view for joining new groups"""
        self.current_view = "join_groups"
        self.content_container.controls.clear()
        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )
        self.content_container.controls.append(back_button)
        self.page.run_task(self.load_joinable_groups)

    async def load_joinable_groups(self):
        """Load and display joinable groups"""
        try:
            self.cached_joinable_groups = await fetch_groups(self.user_id)
            self._render_joinable_groups_list(self.cached_joinable_groups)
        except Exception as ex:
            print("Error loading joinable groups:", ex)

    async def join_group_action(self, group_id):
        """Join a group by ID"""
        try:
            await join_group(self.user_id, group_id)
            self.cached_user_groups = []
            self.cached_joinable_groups = []
            self.page.run_task(self.load_user_groups)
        except Exception as ex:
            print("Error joining group:", ex)

    def show_create_group_dialog(self, e):
        """Show dialog to create a new group"""
        file_picker = ft.FilePicker(on_result=self.on_avatar_picked)
        self.page.overlay.append(file_picker)

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
        """Handle avatar image selection"""
        if not e.files: return
        file = e.files[0]
        if not file.path:
            print("Mobile: File path not available!")
            return
        self.selected_avatar_path = file.path
        b64 = image_to_base64(file.path)
        self.upload_box.content = ft.Image(
            src_base64=b64,
            width=125,
            height=125,
            fit=ft.ImageFit.COVER,
            border_radius=12
        )
        self.page.update()

    async def create_group_action(self):
        """Create a new group with provided details"""
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

    def _restore_group_list(self):
        """Restore the view to the user's group list"""
        self.action_buttons.visible = True
        self.group_navbar.visible = False
        self.page.run_task(self.load_user_groups)

    async def view_group(self):
        """View details of the current group"""
        group = await fetch_group_info(self.current_group_id)
        group_info = group.get("group", {})
        members = group_info.get("members", [])
        admin_id = group_info.get("admin_id")
        current_user_is_admin = (self.user_id == admin_id)

        # Hide top buttons, show navbar
        self.action_buttons.visible = False
        self.group_navbar.visible = True

        def remove_member(e, member):
            self.page.client_storage.set("member_to_remove", member.get("user_id"))
            print(member.get("user_id"))
            self.confirm_dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=18),
                inset_padding=ft.padding.all(20),
                title=ft.Text("Confirm Removal", size=20, weight=ft.FontWeight.BOLD),
                content=ft.Text("Are you sure you want to remove this member from the group?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.confirm_dialog)),
                    ft.TextButton("Remove", on_click=lambda e: self.page.run_task(self.remove_member_from_group))
                ]
            )
            self.page.open(self.confirm_dialog)

        async def leave_group_action(e):
            """Leave the current group"""
            self.confirm_dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=18),
                inset_padding=ft.padding.all(20),
                title=ft.Text("Leave Group", size=20, weight=ft.FontWeight.BOLD),
                content=ft.Text("Are you sure you want to leave this group?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.confirm_dialog)),
                    ft.TextButton(
                        "Leave",
                        on_click=lambda e: self.page.run_task(self.leave_group)
                    ),
                ]
            )
            self.page.open(self.confirm_dialog)

        # Clear current content
        self.content_container.controls.clear()

        # Back button
        self.content_container.controls.append(
            ft.TextButton("← Back to My Groups", on_click=lambda e: self._restore_group_list())
        )

        # Group title with Leave Group button
        self.content_container.controls.append(
            ft.Row(
                controls=[
                    ft.Text(f"Group: {group_info['name']}", size=22, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Leave Group", on_click=leave_group_action, bgcolor=ft.Colors.RED)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        # ListTiles for members
        member_tiles = []

        for member in members:
            is_admin = (member.get("user_id") == admin_id)
            role_text = "Admin" if is_admin else "Member"

            trailing_menu = ft.IconButton(
                icon=ft.Icons.REMOVE_CIRCLE,
                icon_color=ft.Colors.RED,
                visible=current_user_is_admin and not is_admin,
                on_click=lambda e, m=member: remove_member(e, m),
                tooltip="Remove Member"
            )

            tile = ft.ListTile(
                title=ft.Text(f"{member.get('first_name', '-')} {member.get('last_name', '-')}", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(role_text),
                trailing=trailing_menu,
                content_padding=ft.padding.symmetric(vertical=10, horizontal=16),
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE
            )
            member_tiles.append(tile)

        # Wrap in a scrollable column (vertical)
        scrollable_members = ft.Column(
            controls=member_tiles,
            spacing=10,
            expand=True
        )

        self.content_container.controls.append(scrollable_members)
        self.page.update()

    async def leave_group(self):
        """Logic to leave the group"""
        await remove_member(self.user_id, self.current_group_id)  # reuse remove_member API
        self.page.close(self.confirm_dialog)
        self.cached_user_groups = []

        self._restore_group_list()


    async def remove_member_from_group(self):
        member_id = await self.page.client_storage.get_async("member_to_remove")
        await remove_member(member_id, self.current_group_id)

        self.page.close(self.confirm_dialog)
        self.page.run_task(self.view_group)


    def _on_group_nav_change(self, e):
        idx = e.control.selected_index
        if idx == 0:  # Members tab
            self.page.run_task(self.view_group)
        elif idx == 1:  # Images tab
            self.content_container.controls.clear()
            self.content_container.controls.append(ft.Text("Images page content here..."))
            self.page.update()
