from typing import Optional
import flet as ft


def get_video_thumbnail(video_url: str) -> Optional[str]:
    """Get thumbnail URL for a Cloudinary video."""
    if not video_url:
        return None

    return (
        video_url.replace("/video/upload/", "/video/upload/so_0/").rsplit(".", 1)[0]
        + ".jpg"
    )


def build_thumb(file: dict, img_size: int = 100, with_playbtn: bool = True) -> ft.Control:
    """Build a thumbnail control for a given file."""
    url = file.get(
        "file_url"
    )  # Assuming the file dict has a 'file_url' key with the Cloudinary URL
    thumb_url = url  # Default thumbnail is the file itself

    is_video = (
        get_file_type(url) == "video"
    )  # Check if the file is a video to generate a thumbnail
    if is_video:
        thumb_url = get_video_thumbnail(url)

    thumbnail_img = ft.Image(
        src=thumb_url,
        width=img_size,
        height=img_size,
        fit=ft.BoxFit.COVER,
    )

    content = ft.Column(
        controls=[
            ft.Stack(
                alignment=ft.Alignment.CENTER,
                controls=[
                    thumbnail_img,
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PLAY_CIRCLE,
                            size=48,
                            color=ft.Colors.WHITE,
                        ),
                        alignment=ft.Alignment.CENTER,
                        visible=is_video and with_playbtn,
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                ]
            )
        ]
    )

    return ft.Container(
        content=content,
        border_radius=10,
        width=img_size,
        height=img_size,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

def get_file_type(file_url: str) -> Optional[str]:
    """Determine file type based on URL."""
    if not file_url:
        return None

    if "/video/upload/" in file_url:
        return "video"
    if "/image/upload/" in file_url:
        return "image"
    if "/raw/upload/" in file_url:
        return "raw"

    return "unknown"

def cloudinary_to_download_url(url: str) -> str:
    """
    Convert a Cloudinary URL to:
    https://res.cloudinary.com/<cloud>/<resource>/upload/fl_attachment/<public_id>
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    try:
        upload_index = parts.index("upload")
    except ValueError:
        # Not a standard Cloudinary URL
        return url

    # Everything after the last '/' belongs to public_id (may include folders)
    # Remove transformations and versioning
    public_id_parts = []

    for part in parts[upload_index + 1:]:
        # Skip transformations
        if "," in part or part.startswith("w_") or part.startswith("q_") or part.startswith("f_"):
            continue
        # Skip versioning
        if part.startswith("v") and part[1:].isdigit():
            continue
        public_id_parts.append(part)

    new_parts = (
        parts[:upload_index + 1]
        + ["fl_attachment"]
        + public_id_parts
    )

    new_path = "/" + "/".join(new_parts)
    return parsed._replace(path=new_path).geturl()

if __name__ == "__main__":
    # Example usage
    video_url = "https://res.cloudinary.com/demo/video/upload/v1610000000/sample.mp4"
    image_url = "https://res.cloudinary.com/demo/image/upload/v1610000000/sample.jpg"

    print(cloudinary_to_download_url(video_url))
    print(cloudinary_to_download_url(image_url))    
