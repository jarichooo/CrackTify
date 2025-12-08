import flet as ft
from typing import List

from services.crack_service import *


class DetectionHistoryPage:
    def __init__(self, page: ft.Page):
        self.page = page

        # Load existing or create sample data
        self.history = self.page.client_storage.get("history")
        if not self.history:
            self.history = self.generate_sample_data()
            self.page.client_storage.set("history", self.history)

    # SAMPLE DATA POPULATOR
    def generate_sample_data(self):
        # A 1x1 black pixel base64 image (safe small sample)
        sample_base64_img = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
            "DQottAAAAABJRU5ErkJggg=="
        )

        return {
            "2025-12-05 14:00": {
                "file_base64": sample_base64_img,
                "file_name": "meteor_sample.jpg",
                "result": "Meteor detected",
            },
            "2025-12-04 10:33": {
                "file_base64": sample_base64_img,
                "file_name": "object_02.png",
                "result": "Not a meteor",
            },
        }

    # MAIN BUILD
    def build(self) -> List[ft.Column]:

        # Clear All button
        self.clear_btn = ft.FilledButton(
            "Clear All History",
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self.clear_all,
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
        )

        # Scrollable list
        self.listview = ft.ListView(
            expand=True,
            spacing=10,
            controls=[]
        )

        # Container wrapper
        self.container = ft.Column([
            self.clear_btn,
            self.listview,
        ], expand=True)

        self.on_show()
        return [self.container]

    # SHOW HISTORY
    def on_show(self):

        self.listview.controls.clear()

        if not self.history:
            self.listview.controls.append(
                ft.Text("No detection history available.", italic=True)
            )
        else:
            for date, data in self.history.items():

                file_name = data.get("file_name", "Unknown")
                result = data.get("result", "No Result")
                file_base64 = data.get("file_base64")

                # Thumbnail preview
                image_control = ft.Image(
                    src_base64=file_base64,
                    width=80,
                    height=80,
                    fit=ft.ImageFit.COVER,
                )

                # Collapse panel (Expandable)
                panel = ft.ExpansionTile(
                    title=ft.Text(f"{file_name} — {result}"),
                    subtitle=ft.Text(date),
                    controls=[
                        ft.Row(
                            [
                                image_control,
                                ft.Column(
                                    [
                                        ft.Text(f"File Name: {file_name}"),
                                        ft.Text(f"Result: {result}"),
                                        ft.Text(f"Date: {date}"),
                                        ft.FilledButton(
                                            "Delete",
                                            icon=ft.Icons.DELETE,
                                            bgcolor=ft.Colors.RED_300,
                                            color=ft.Colors.WHITE,
                                            on_click=lambda e, d=date: self.delete_item(d)
                                        )
                                    ],
                                    spacing=5,
                                )
                            ]
                        )
                    ],
                )

                self.listview.controls.append(panel)

        self.page.update()

    # DELETE A SINGLE ENTRY
    def delete_item(self, date):
        if date in self.history:
            del self.history[date]
            self.page.client_storage.set("history", self.history)
            self.on_show()

    # CLEAR ALL
    def clear_all(self, e):
        self.history = {}
        self.page.client_storage.set("history", self.history)
        self.on_show()

    # HIDE EVENT
    def on_hide(self):
        print("Current history:", self.history)
