"""
Main server application

HVR 6.0 Multi-Agent System server with REST API and WebSocket support.
"""

import asyncio
import json
import os
import signal
from contextlib import asynccontextmanager
from typing import Set

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.server.agents.agent_orchestrator import AgentOrchestrator
from src.server.api import (
    create_agents_router,
    create_health_router,
    create_jobs_router,
    create_tasks_router,
)
from src.server.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger("main")

# Global orchestrator instance
orchestrator: AgentOrchestrator = None
websocket_connections: Set[WebSocket] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown tasks.
    """
    global orchestrator

    # Startup
    logger.info("Starting HVR 6.0 Multi-Agent System")
    orchestrator = AgentOrchestrator()

    # Register event handlers
    orchestrator.on("taskStarted", lambda data: broadcast_websocket({"type": "taskStarted", "data": data}))
    orchestrator.on("taskCompleted", lambda data: broadcast_websocket({"type": "taskCompleted", "data": data}))
    orchestrator.on("taskFailed", lambda data: broadcast_websocket({"type": "taskFailed", "data": data}))

    # Start orchestrator
    orchestrator.start()
    logger.info("Agent Orchestrator started")

    # Setup routes with initialized orchestrator
    app.include_router(create_agents_router(orchestrator))
    app.include_router(create_tasks_router(orchestrator))
    app.include_router(create_jobs_router(orchestrator))
    app.include_router(create_health_router(orchestrator))
    logger.info("API routes configured")

    yield

    # Shutdown
    logger.info("Shutting down HVR 6.0 Multi-Agent System")
    orchestrator.stop()
    logger.info("Agent Orchestrator stopped")


# Create FastAPI application
app = FastAPI(
    title="HVR 6.0 Client Agents API",
    version="1.0.0",
    description="Python-based HVR 6.0 Client with Multi-Agent Architecture for SAP Data Replication",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers - moved to after app creation
# Will be called in lifespan context


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "HVR 6.0 Client Agents API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "agents": "/api/agents",
            "tasks": "/api/tasks",
            "jobs": "/api/jobs",
            "health": "/api/health",
            "websocket": "/ws",
        },
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Clients can connect to receive real-time task and agent updates.
    """
    await websocket.accept()
    websocket_connections.add(websocket)
    logger.info("WebSocket client connected")

    try:
        # Send initial connection message
        await websocket.send_json(
            {"type": "connected", "message": "Connected to HVR 6.0 Agent System"}
        )

        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"WebSocket received: {data}")
            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_connections.discard(websocket)
        logger.info("WebSocket client disconnected")


def broadcast_websocket(message: dict):
    """
    Broadcast message to all connected WebSocket clients

    Args:
        message: Message to broadcast
    """
    if not websocket_connections:
        return

    disconnected = set()

    for websocket in websocket_connections:
        try:
            # Create task to send message asynchronously
            asyncio.create_task(websocket.send_json(message))
        except Exception as e:
            logger.error(f"Error broadcasting to websocket: {e}")
            disconnected.add(websocket)

    # Remove disconnected clients
    websocket_connections.difference_update(disconnected)


def main():
    """
    Main entry point for running the server
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    environment = os.getenv("ENVIRONMENT", "development")

    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Environment: {environment}")

    import uvicorn

    uvicorn.run(
        "src.server.main:app",
        host=host,
        port=port,
        reload=environment == "development",
        log_level="info",
    )


if __name__ == "__main__":
    main()
