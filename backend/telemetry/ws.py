"""
AI Job Hunter - Live Agent Telemetry & Terminal WebSocket
Streams real-time multi-agent execution events, log lines, and node telemetry
to the 3D Glassmorphic Command Center.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.utils.logger import get_logger

logger = get_logger("telemetry.ws")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


class TelemetryConnectionManager:
    """Manages active WebSocket connections for live telemetry streaming."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("Telemetry client connected", total=len(self.active_connections))

        # Send initial connected greeting
        await websocket.send_json({
            "type": "SYSTEM_CONNECTED",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": "Connected to CareerOps Real-Time Telemetry Stream",
            "active_swarm_nodes": [
                "Profile Ingest", "Omni Discovery", "7-Factor Matcher",
                "Gemini Hub", "Playwright Bot", "Gmail Outreach", "Inbound Sync"
            ],
        })

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info("Telemetry client disconnected", total=len(self.active_connections))

    async def broadcast_event(self, event_type: str, module: str, message: str, payload: dict | None = None) -> None:
        """Broadcast an event to all connected dashboard terminals."""
        data = {
            "type": event_type,
            "module": module,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "payload": payload or {},
        }
        dead_connections = set()
        for conn in self.active_connections:
            try:
                await conn.send_json(data)
            except Exception:
                dead_connections.add(conn)

        for dead in dead_connections:
            self.active_connections.discard(dead)


manager = TelemetryConnectionManager()


@router.websocket("/ws")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive loop
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.now().strftime("%H:%M:%S")})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
