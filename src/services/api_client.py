import httpx
from typing import Dict, Any
from config import Config

# Base API URL
api_url = Config.API_BASE_URL
print(f"[DEBUG] API Base URL: {api_url}")


async def verify_connection() -> bool:
    """Check if the API server is reachable."""
    print("[DEBUG] Verifying API connection...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{api_url}/")
            print(f"[DEBUG] Response status code: {response.status_code}")
            return response.status_code == 200
    except httpx.RequestError as e:
        print(f"[DEBUG] Connection failed: {e}")
        return False


async def post_request(endpoint: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
    url = f"{api_url.rstrip('/')}/{endpoint.lstrip('/')}"  # Ensure no double slash
    print(f"[DEBUG] POST request URL: {url}")
    print(f"[DEBUG] POST request data: {data}")
    print(f"[DEBUG] POST request headers: {headers}")

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            print(f"[DEBUG] POST response status: {response.status_code}")
            response.raise_for_status()
            json_response = response.json()
            print(f"[DEBUG] POST response JSON: {json_response}")
            return json_response

        except httpx.HTTPStatusError as e:
            print(f"[DEBUG] HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "status_code": e.response.status_code,
                "error": e.response.text,
            }

        except httpx.RequestError as e:
            print(f"[DEBUG] Network error: {e}")
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
    """
    url = f"{api_url}{endpoint}"
    print(f"[DEBUG] GET request URL: {url}")
    print(f"[DEBUG] GET request headers: {headers}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            print(f"[DEBUG] GET response status: {response.status_code}")
            json_response = response.json()
            print(f"[DEBUG] GET response JSON: {json_response}")
            return json_response

    except httpx.RequestError as e:
        print(f"[DEBUG] GET request network error: {e}")
        return {"success": False, "error": f"Network error: {e}"}
    except Exception as e:
        print(f"[DEBUG] GET request exception: {e}")
        return {"success": False, "error": str(e)}