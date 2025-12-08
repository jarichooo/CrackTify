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
from services.crack_service import fetch_cracks_service, delete_crack_service
from widgets.inputs import AppTextField
from utils.image_utils import image_to_base64, base64_to_image


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
        print("Groups refreshed.")

    def filter_content(self, query: str):
        query_lower = query.lower()
        if self.current_view == "join_groups":
            filtered_joinable = [
                g for g in self.cached_joinable_groups.get("groups", [])
                if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
            ]
            self._render_joinable_groups_list({"groups": filtered_joinable}, search_mode=True)
            return
     
        filtered_user = [
            g for g in self.cached_user_groups.get("groups", [])
            if query_lower in g["name"].lower() or query_lower in g.get("description", "").lower()
        ]
        self.content_container.controls.clear()
        self.content_container.controls.append(ft.TextButton("My Groups"))
        self._render_user_groups_list(filtered_user, search_mode=True)
        self.page.update()

    def _render_user_groups_list(self, groups_data, search_mode=False):
        """Render the list of user's groups"""
        if not groups_data and not search_mode:
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
        
        if not groups_data and search_mode:
            self.content_container.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=100, color=ft.Colors.GREY),
                            ft.Text("No group found.", size=20, color=ft.Colors.GREY),
                        ],
                    ),
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

    def _render_joinable_groups_list(self, joinable_data, search_mode=False):
        self.content_container.controls.clear()
        back_button = ft.TextButton(
            "← Back to My Groups",
            on_click=lambda e: self.page.run_task(self.load_user_groups)
        )
        self.content_container.controls.append(back_button)

        if not joinable_data.get("groups") and not search_mode:
            self.content_container.controls.append(
                ft.Column(
                    [ft.Text("No joinable groups available.", size=16, color=ft.Colors.GREY)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            )
            self.page.update()
            return
        
        if not joinable_data.get("groups") and search_mode:
            self.content_container.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=100, color=ft.Colors.GREY),
                            ft.Text("No groups found.", size=20, color=ft.Colors.GREY),
                        ],
                    ),
            )
            )
            self.page.update()
            return

        for g in joinable_data.get("groups", []):
            gid = g["id"]
            members_count = len(g.get("members", []))

            def join_with_pin(e, group_id=gid):
                self.pin_input = AppTextField(label="Enter PIN", password=True, keyboard_type=ft.KeyboardType.NUMBER, on_change=lambda e: self.pin_input.clear_error())
                
                self.join_dialog = ft.AlertDialog(
                    modal=True,
                    shape=ft.RoundedRectangleBorder(radius=18),
                    inset_padding=ft.padding.all(20),
                    title=ft.Text(g['name'], size=18, weight=ft.FontWeight.BOLD),
                    content=self.pin_input,
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.join_dialog)),
                        ft.TextButton(
                            "Join",
                            on_click=self.get_joining_pin,
                            data={"group_id": group_id, "pin_input": self.pin_input}

                        )
                    ]
                )
                self.page.open(self.join_dialog)

            tile = ft.ListTile(
                title=ft.Text(g["name"], size=18, weight="bold"),
                subtitle=ft.Text(f"👥 Members: {members_count}"),
                trailing=ft.ElevatedButton("Join", width=80, on_click=join_with_pin),
                content_padding=ft.padding.symmetric(vertical=10, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            )

            self.content_container.controls.append(tile)

        self.page.update()

    def get_joining_pin(self, e):
        """Join a group using PIN from dialog input"""
        # self.page.close(e.control.page.dialog)
        data = e.control.data

        self.joining_group_id = data.get("group_id")
        self.joining_pin = data.get("pin_input").value

        self.page.run_task(self.run_join_group)

    async def run_join_group(self):
        """Join a group by ID"""
        try:
            resp = await join_group(self.user_id, self.joining_group_id, self.joining_pin)
            if not resp.get("success"):
                self.pin_input.error_text = resp.get("message")
                self.pin_input.update()
                return
            
            self.page.close(self.join_dialog)
            self.cached_user_groups = []
            self.cached_joinable_groups = []

            self.current_view = "my_groups"
            self.current_group_id = self.joining_group_id
            self.page.run_task(self.view_group)
            
        except Exception as ex:
            print("Error joining group:", ex)


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
        """Show dialog to create a new group with Name and PIN only"""
        self.group_name_input = AppTextField(
            label="Group Name",
            on_change=lambda e: self.group_name_input.clear_error()
        )
        self.group_pin_input = AppTextField(
            label="PIN", 
            password=True,
            keyboard_type=ft.KeyboardType.NUMBER, 
            on_change=lambda e: self.group_pin_input.clear_error()
        ) 

        self.dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=18),
            inset_padding=ft.padding.all(20),
            title=ft.Text("Create New Group", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=10,
                height=150,
                controls=[self.group_name_input, self.group_pin_input]
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dialog)),
                ft.TextButton("Create", on_click=lambda e: self.page.run_task(self.create_group_action))
            ]
        )
        self.page.open(self.dialog)

    async def create_group_action(self):
        """Create a new group using name and pin"""
        name = self.group_name_input.value
        pin = self.group_pin_input.value

        if not name:
            self.group_name_input.error_text = "Group name is required"
            self.page.update()
            return
        
        if not pin:
            self.group_pin_input.error_text = "PIN is required"
            self.page.update()
            return

        await create_group(name=name, pin=pin, admin_id=self.user_id)
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
                    ft.Text(group_info['name'], size=22, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Leave Group", color=ft.Colors.WHITE, on_click=leave_group_action, bgcolor=ft.Colors.RED)
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
                icon=ft.Icons.PERSON_REMOVE,
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
        """Remove a member from the current group"""
        member_id = await self.page.client_storage.get_async("member_to_remove")
        await remove_member(member_id, self.current_group_id)

        self.page.close(self.confirm_dialog)
        self.page.run_task(self.view_group)

    def _on_group_nav_change(self, e):
        """Handle navigation bar tab changes"""
        idx = e.control.selected_index
        if idx == 0:  # Members tab
            self.page.run_task(self.view_group)
        elif idx == 1:  # Images tab
            self.content_container.controls.clear()
            self.page.run_task(self.view_group_images)

            self.page.update()

    async def view_group_images(self):
        """View crack images for the current group."""

        response = await fetch_cracks_service(self.current_group_id)
        cracks = response.get("cracks") if response else []

        self.content_container.controls.clear()

        if not cracks:
            self.content_container.controls.append(
                ft.Container(
                    content=ft.Text("No cracks detected yet.", size=20),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
            self.page.update()
            return

        grid_items = []

        for crack in cracks:
            img_base64 = crack.get("image_base64")
            severity = crack.get("severity", "Unknown")
            crack_id = crack.get("id")
            uploader_id = crack.get("user_id")

            image_control = ft.Image(
                src_base64=img_base64,
                width=140,
                height=140,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(12),
            )

            can_delete = (self.user_id == uploader_id or self.user_id == self.current_group_admin)

            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED,
                visible=can_delete,
                tooltip="Delete crack",
                on_click=lambda e, cid=crack_id: self._prepare_delete_crack(cid)
            )

            tile = ft.Container(
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
                padding=10,
                border_radius=12,
                content=ft.Column(
                    controls=[
                        image_control,
                        ft.Text(f"Severity: {severity}", weight=ft.FontWeight.BOLD),
                        delete_btn
                    ],
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

            grid_items.append(tile)

        grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=200,
            spacing=10,
            run_spacing=10,
            controls=grid_items
        )

        self.content_container.controls.append(grid)
        self.page.update()

    def _prepare_delete_crack(self, crack_id):
        self.page.client_storage.set("crack_to_delete", crack_id)
        self.page.run_task(self.delete_crack_action)

    async def delete_crack_action(self):
        crack_id = await self.page.client_storage.get_async("crack_to_delete")
        if not crack_id:
            return

        response = delete_crack_service(crack_id, self.user_id, db=None)

        if response.get("success"):
            print("Crack deleted:", crack_id)
        else:
            print("Delete failed:", response.get("message"))

        await self.view_group_images()
