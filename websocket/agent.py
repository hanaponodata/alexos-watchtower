"""
websocket/agent.py
WebSocket handler for Watchtower agent connections.
Manages real-time agent event ingestion, heartbeat, and status reporting.
"""

import logging
from typing import Dict, Any
from fastapi import WebSocket
from .server import WebSocketServer

class AgentSocketHandler:
    def __init__(self, ws_server: WebSocketServer):
        self.ws_server = ws_server
        self.logger = logging.getLogger("watchtower.ws.agent")

    async def handle(self, client_id: str, websocket: WebSocket):
        """
        Handle the agent's WebSocket session.
        """
        await self.ws_server.connect(client_id, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                self.logger.debug(f"Agent WS message from {client_id}: {data}")
                if data.get("action") == "heartbeat":
                    # Handle agent heartbeat logic here
                    await self.ws_server.send_message(client_id, {"msg": "heartbeat_ack"})
                elif data.get("action") == "event":
                    # Optionally ingest events directly over WS
                    await self.ws_server.send_message(client_id, {"msg": "event_received"})
                # Add more actions as needed for agent protocol
        except Exception as e:
            self.logger.warning(f"Agent WS error ({client_id}): {e}")
        finally:
            self.ws_server.disconnect(client_id)

if __name__ == "__main__":
    print("AgentSocketHandler module ready.")
