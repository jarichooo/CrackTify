import httpx
from config import Config

api_url = Config.API_BASE_URL

async def send_otp(email: str, name: str):
    data = {"email": email, "name": name}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url=f"{api_url}/otp/send-otp", json=data)
            response.raise_for_status()

            return response.json()
        
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")
            
            return {"success": False, "error": str(e)}

async def verify_otp(email: str, entered_otp: str):
    data = {"email": email, "entered_otp": entered_otp}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url=f"{api_url}/otp/verify-otp", json=data)
            response.raise_for_status()

            return response.json()
        
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")
            
            return {"success": False, "error": str(e)}