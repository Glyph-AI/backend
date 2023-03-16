import asyncio
import time


class Glyph:
    def __init__(self):
        self.sleep_time = 1

    async def process_message(self, incoming_message: str):
        message = await asyncio.sleep(self.sleep_time, f"Message received: {incoming_message}")

        return message
