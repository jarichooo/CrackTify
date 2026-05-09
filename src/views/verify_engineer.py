import flet as ft
from dataclasses import dataclass, field

from services.file_service import upload_file
from views.template import TemplatePage
from widgets.buttons import BackButton
from widgets.inputs import TextField
from widgets.buttons import PrimaryButton

from services.engineer_service import verify_engineer

from model.user import User 


@dataclass
class State:
    file_path: ft.FilePicker | None = None
    picked_file: list[ft.FilePickerFile] = field(default_factory=list)


class VerifyEngineerPage(TemplatePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)

        self.state = State()
        self.user = User.to_dict()  # Get user data as a dictionary

    def build(self) -> ft.View:
        """Builds the engineer verification page view with app bar and body content for uploading verification documents."""
        self.back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Back",
            on_click=self.cancel_registration,
        )

        self.license_field = TextField(
            width=400,
            label="Professional License Number",
            hint_text="Enter your professional license number",
        )

        self.preview_image = ft.Image(
            src="placeholder.png",  # starts empty, updated after file is picked
            fit=ft.BoxFit.CONTAIN,
            error_content=ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.padding.all(16),
                content=ft.Container(
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.UPLOAD_FILE, size=40, color=ft.Colors.GREY),
                            ft.Text("Upload your verification document", color=ft.Colors.GREY, size=12),
                        ],
                    ),
                ),
            )
        )

        self.upload_container = ft.Container(
            on_click=self.handle_file_pick,
            height=250,
            width=400,
            alignment=ft.Alignment.CENTER,
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=10,
            content=ft.InteractiveViewer(
                ft.Container(
                    width=400,
                    height=250,
                    content=self.preview_image,
                ),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
        )

        self.verify_button = PrimaryButton(
            text="Submit Verification",
            on_click=self.do_verify_engineer,
        )

        self.body = ft.Column(

            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=500,  # max width so it doesn't stretch on tablets/desktop
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    content=ft.Column(
                        spacing=16,  # consistent gap between each element
                        controls=[
                            ft.Text(
                                "As an structural engineer, you need to upload additional verification "
                                "documents. Please provide the supporting documentation to complete your registration.",
                                size=14,
                            ),
                            ft.Divider(),
                            self.license_field,
                            self.upload_container,
                            ft.Divider(),
                            self.verify_button,
                        ],
                    ),
                )
            ],
        )

        return self.layout(
            route="/verify-engineer",
            appbar=ft.AppBar(
                title=ft.Text("Extra Verification Required"),
                leading=self.back_button,
            ),
            controls=[self.body],
        )

    def cancel_registration(self, e):
        self.cancel_dialog = ft.AlertDialog(
            title=ft.Text("Cancel Verification"),
            content=ft.Text(
                "Are you sure you want to cancel the verification process? You can always complete it later from your profile settings."
            ),
            actions=[
                ft.TextButton("No", on_click=lambda e: self.page.pop_dialog()),
                ft.TextButton("Yes", on_click=lambda e: self.page.views.pop()),
            ],
        )
        self.page.show_dialog(self.cancel_dialog)

    async def handle_file_pick(self, e):
        """Handles the file selection and updates the state with the picked file."""
        self.state.file_path = ft.FilePicker()

        files = await self.state.file_path.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.MEDIA,
            allowed_extensions=["jpg", "jpeg", "png"],  # fixed from file_types
        )
        if files:
            self.state.picked_file = files[0]
            self.preview_image.src = self.state.picked_file.path  # update preview

        self.page.update()

    async def do_verify_engineer(self, e):
        """Handles the verification process for engineers, including validating the license number and uploaded document."""
        if not self.license_field.value or not self.state.picked_file:
            self.error_dialog = ft.AlertDialog(
                title=ft.Text("Missing Information"),
                content=ft.Text(
                    "Please provide both your professional license number and a verification document to proceed."
                ),
                actions=[ft.TextButton("OK", on_click=lambda e: (
                    setattr(self.error_dialog, "open", False), self.page.update()
                ))],
            )
            self.page.show_dialog(self.error_dialog)
            return

        self.show_loading("Submitting...")

        resp = await upload_file(self.state.picked_file.path)
        if not resp.get("success"):
            error_dialog = ft.AlertDialog(
                title=ft.Text("Upload Failed"),
                content=ft.Text(f"Failed to upload document: {resp.get('message', 'Unknown error')}"),
                actions=[ft.TextButton("OK", on_click=lambda e: (
                    setattr(error_dialog, "open", False), self.page.update()
                ))],
            )
            self.page.show_dialog(error_dialog)
            return

        ve_resp = await verify_engineer(
            user_id=self.user.get("id"),
            license_number=self.license_field.value,
            document_url=resp.get("url"), 
        )

        if not ve_resp.get("success"):
            error_dialog = ft.AlertDialog(
                title=ft.Text("Verification Failed"),
                content=ft.Text(f"Verification failed: {ve_resp.get('message', 'Unknown error')}"),
                actions=[ft.TextButton("OK", on_click=lambda e: (
                    setattr(error_dialog, "open", False), self.page.update()
                ))],
            )
            self.hide_loading()
            self.page.show_dialog(error_dialog)
            return

        submitted_dialog = ft.AlertDialog(
            title=ft.Text("Verification Submitted"),
            content=ft.Text(
                "Your verification documents have been submitted successfully. We will review your information and get back to you shortly."
            ),
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.views.pop())],
        )

        self.hide_loading()
        self.page.show_dialog(submitted_dialog)