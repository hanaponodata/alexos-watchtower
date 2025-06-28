"""
websocket/server.py
Core WebSocket server for Watchtower.
Handles client connections, session management, and real-time event routing.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

class WebSocketServer:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.logger = logging.getLogger("watchtower.websocket")

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.logger.info(f"WebSocket disconnected: {client_id}")

    async def send_message(self, client_id: str, message: Dict[str, Any]):
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_json(message)
            self.logger.debug(f"Sent WS message to {client_id}: {message}")

    async def broadcast(self, message: Dict[str, Any]):
        for client_id, ws in list(self.active_connections.items()):
            try:
                await ws.send_json(message)
                self.logger.debug(f"Broadcast WS message to {client_id}: {message}")
            except Exception as e:
                self.logger.warning(f"Failed to send to {client_id}: {e}")

    async def handler(
        self,
        client_id: str,
        websocket: WebSocket,
        on_message: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ):
        await self.connect(client_id, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                self.logger.debug(f"WS message from {client_id}: {data}")
                if on_message:
                    await run_in_threadpool(on_message, data)
        except WebSocketDisconnect:
            self.disconnect(client_id)
        except Exception as e:
            self.logger.error(f"WebSocket error ({client_id}): {e}")
            self.disconnect(client_id)

if __name__ == "__main__":
    print("WebSocketServer module ready for FastAPI integration.")
