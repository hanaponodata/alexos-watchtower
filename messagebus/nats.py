"""
messagebus/nats.py
Enterprise-grade NATS message bus adapter for Watchtower.
Handles publish, subscribe, and event routing over NATS clusters.
"""

from typing import Callable, Optional, Any
import asyncio

try:
    import nats
except ImportError:
    nats = None

class NATSBus:
    def __init__(self, url: str = "nats://localhost:4222", loop: Optional[asyncio.AbstractEventLoop] = None):
        self.url = url
        self.loop = loop or asyncio.get_event_loop()
        self.nc = None

    async def connect(self):
        if not nats:
            raise ImportError("nats-py is not installed")
        self.nc = await nats.connect(self.url, loop=self.loop)

    async def publish(self, subject: str, message: bytes):
        if self.nc is None:
            await self.connect()
        await self.nc.publish(subject, message)

    async def subscribe(self, subject: str, cb: Callable[[Any], None]):
        if self.nc is None:
            await self.connect()
        await self.nc.subscribe(subject, cb=cb)

    async def close(self):
        if self.nc:
            await self.nc.close()
            self.nc = None

if __name__ == "__main__":
    print("NATSBus requires async event loop and nats-py installed.")
