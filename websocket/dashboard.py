"""
websocket/dashboard.py
WebSocket handler for the Watchtower dashboard UI.
Streams live event, status, and audit data to dashboard clients in real-time.
"""

import logging
from typing import Dict, Any
from fastapi import WebSocket
from .server import WebSocketServer

class DashboardSocketHandler:
    def __init__(self, ws_server: WebSocketServer):
        self.ws_server = ws_server
        self.logger = logging.getLogger("watchtower.ws.dashboard")

    async def handle(self, client_id: str, websocket: WebSocket):
        """
        Handle the dashboard client's WebSocket session.
        """
        await self.ws_server.connect(client_id, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                self.logger.debug(f"Dashboard WS message from {client_id}: {data}")
                # Optionally handle dashboard-originated actions
                if data.get("action") == "subscribe":
                    # Handle event or data subscription requests
                    await self.ws_server.send_message(client_id, {"msg": "subscribed"})
                elif data.get("action") == "ping":
                    await self.ws_server.send_message(client_id, {"msg": "pong"})
                # Add more actions as needed
        except Exception as e:
            self.logger.warning(f"Dashboard WS error ({client_id}): {e}")
        finally:
            self.ws_server.disconnect(client_id)

if __name__ == "__main__":
    print("DashboardSocketHandler module ready.")
