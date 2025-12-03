import httpx
from typing import Dict, Any
from config import Config

# Base API URL
api_url = Config.API_BASE_URL

async def post_request(
    endpoint: str,
    data: Dict[str, Any],
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Reusable POST request helper with consistent error handling.
    
    Args:
        endpoint: API endpoint (e.g., "/otp/send-otp")
        data: JSON payload to send
        headers: Optional HTTP headers
    
    Returns:
        dict: Response JSON or error info
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(f"{api_url}{endpoint}", json=data, headers=headers)
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
    Reusable GET request helper with consistent error handling.
    
    Args:
        endpoint: API endpoint (e.g., "/profile")
        headers: Optional HTTP headers 
    Returns:
        dict: Response JSON or error info
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(f"{api_url}{endpoint}", headers=headers)
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
