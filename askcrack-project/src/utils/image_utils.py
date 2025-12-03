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