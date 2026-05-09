import asyncio
import json
import websockets
from config import Config


class WSClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL.replace("http", "ws")
        self._task = None

    def start(self, user_id: str, on_message):
        self._task = asyncio.create_task(self._listen(user_id, on_message))

    def stop(self):
        if self._task:
            self._task.cancel()

    async def _listen(self, user_id: str, on_message):
        uri = f"{self.base_url}/ws/{user_id}"
        async with websockets.connect(uri) as ws:
            async for raw in ws:
                data = json.loads(raw)
                await on_message(data)
