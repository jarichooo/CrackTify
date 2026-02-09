from typing import Optional

def get_video_thumbnail(video_url: str) -> Optional[str]:
    """Get thumbnail URL for a Cloudinary video."""
    if not video_url:
        return None

    return video_url.replace(
        "/video/upload/", "/video/upload/so_0/"
    ).rsplit(".", 1)[0] + ".jpg"

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
