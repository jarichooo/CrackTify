import httpx
from typing import Dict, Any
from config import Config

# Base API URL
api_url = Config.API_BASE_URL


async def verify_connection() -> bool:
    """Check if the API server is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{api_url}/")
            return response.status_code == 200
    except httpx.RequestError:
        return False

async def post_request(endpoint: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
    url = f"{api_url.rstrip('/')}/{endpoint.lstrip('/')}"  # Ensure no double slash

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "status_code": e.response.status_code,
                "error": e.response.text,
            }

        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Network error: {e}",
            }

async def get_request(
    endpoint: str,
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Reusable GET request helper that preserves backend 'success' field.

    Args:
        endpoint: API endpoint (e.g., "/profile")
        headers: Optional HTTP headers

    Returns:
        dict: Server JSON response, or a dict with success=False if network error
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{api_url}{endpoint}", headers=headers)
            # Do NOT raise for status — preserve backend success field
            return response.json()
    except httpx.RequestError as e:
        return {"success": False, "error": f"Network error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
