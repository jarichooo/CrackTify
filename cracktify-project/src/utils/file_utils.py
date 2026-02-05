import io
import base64
from PIL import Image
from pathlib import Path

from typing import Optional

def image_to_base64(file_path: Path, size=(480, 480)) -> str:
    """Convert an image file to a base64 string after resizing."""
    try:
        img = Image.open(file_path)
        img.thumbnail(size)
        buffer = io.BytesIO()
        img.save(buffer, format=img.format)

        return base64.b64encode(buffer.getvalue()).decode()
    
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return ""

def base64_to_image(base64_str: str, output_path: Path) -> str:
    """Decode base64 string and save it to a file."""
    if not base64_str:
        return None

    # Ensure the directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Remove base64 prefix if present
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]

    # Decode
    image_bytes = base64.b64decode(base64_str)

    # Write to file
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return output_path


def extract_video_thumbnail(video_path: Path) -> Optional[Path]:
    """
    Extracts the first frame of a video as a thumbnail image.
    Works on both Windows (desktop) and Android.
    """
    import sys
    thumb_dir = Path(__file__).parent.parent / "assets" / "thumbnails"
    thumb_dir.mkdir(exist_ok=True)
    thumb_path = thumb_dir / f"{video_path.stem}.jpg"

    if sys.platform == "android":
        # Android method
        try:
            from jnius import autoclass
            MediaMetadataRetriever = autoclass("android.media.MediaMetadataRetriever")
            Bitmap = autoclass("android.graphics.Bitmap")
            FileOutputStream = autoclass("java.io.FileOutputStream")
            File = autoclass("java.io.File")

            retriever = MediaMetadataRetriever()
            retriever.setDataSource(str(video_path))
            bitmap = retriever.getFrameAtTime(1000000, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)

            if bitmap:
                out = FileOutputStream(File(str(thumb_path)))
                bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
                out.flush()
                out.close()
            retriever.release()
            return thumb_path
        except Exception as e:
            print(f"Android thumbnail error: {e}")
            return None

    else:
        # Desktop method using OpenCV
        try:
            import cv2

            cap = cv2.VideoCapture(str(video_path))
            success, frame = cap.read()
            if success:
                cv2.imwrite(str(thumb_path), frame)
                cap.release()
                return thumb_path
            cap.release()
            return None
        except Exception as e:
            print(f"Desktop thumbnail error: {e}")
            return None


# def extract_video_thumbnail_android(video_path: Path) -> Path:
#     """Extracts the first frame of a video as a thumbnail image on Android."""
#     from jnius import autoclass, cast

#     MediaMetadataRetriever = autoclass("android.media.MediaMetadataRetriever")
#     Bitmap = autoclass("android.graphics.Bitmap")
#     FileOutputStream = autoclass("java.io.FileOutputStream")
#     File = autoclass("java.io.File")

#     retriever = MediaMetadataRetriever() # Create retriever instance
#     try:
#         retriever.setDataSource(video_path)

#         bitmap = retriever.getFrameAtTime(1000000, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)  # first frame at 1 second (in microseconds)

#         thumb_dir = Path(__file__).parent / "thumbnails"
#         thumb_path = thumb_dir / f"{video_path.stem}.jpg"

#         if bitmap:
#             out = FileOutputStream(File(thumb_path))
#             bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
#             out.flush()
#             out.close()
#             print(f"Thumbnail saved to {thumb_path}")


#     except Exception as e:
#         print(f"Error extracting thumbnail from {video_path}: {e}")
#         return None

#     finally:
#         retriever.release()
#         return thumb_path

if __name__ == "__main__":
    # Test the functions
    test_image_path = Path("C:/Users/Admin/Downloads/346569.png")
    base64_str = image_to_base64(test_image_path)
    print(base64_str)

    # output_image_path = Path("output_image.png")
    # saved_path = base64_to_image(base64_str, output_image_path)
    # print("Image saved to:", saved_path)