from pathlib import Path
import io
import base64
from PIL import Image

def image_to_base64(file_path: Path, size=(240, 240)) -> str:
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


if __name__ == "__main__":
    # Test the functions
    test_image_path = "C:/Users/Admin/Downloads/346569.png"
    base64_str = image_to_base64(test_image_path)
    print(base64_str)

    # output_image_path = Path("output_image.png")
    # saved_path = base64_to_image(base64_str, output_image_path)
    # print("Image saved to:", saved_path)