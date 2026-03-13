import httpx
from pathlib import Path
from config import Config

API_BASE_URL = Config.API_BASE_URL


async def upload_file(file_path: str | Path) -> dict:
    """
    Uploads a file to backend server (multipart/form-data).
    Backend uploads it to Cloudinary.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    url = f"{API_BASE_URL.rstrip('/')}/upload/file"
    timeout = httpx.Timeout(60.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        with file_path.open("rb") as f:
            files = {
                "file": (
                    file_path.name,
                    f,
                    "application/octet-stream",
                )
            }

            response = await client.post(url, files=files)

        # handle non-2xx responses clearly
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Upload failed {e.response.status_code}: {e.response.text}"
            ) from e

        return response.json()
