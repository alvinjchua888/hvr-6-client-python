"""
Tasks API endpoints
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.server.agents.agent_orchestrator import AgentOrchestrator
from src.server.utils.logger import get_logger
from src.shared.types import AgentTask, AgentType

logger = get_logger("api.tasks")


class TaskSubmission(BaseModel):
    """Task submission request model"""

    agent_type: AgentType = Field(alias="agentType")
    action: str
    parameters: Dict[str, Any]
    priority: int = 5

    class Config:
        populate_by_name = True


def create_tasks_router(orchestrator: AgentOrchestrator) -> APIRouter:
    """
    Create tasks API router

    Args:
        orchestrator: Agent orchestrator instance

    Returns:
        Configured router
    """
    router = APIRouter(prefix="/api/tasks", tags=["tasks"])

    @router.post("/", response_model=dict, status_code=201)
    async def submit_task(task_data: TaskSubmission) -> dict:
        """Submit a new task"""
        try:
            # Create task
            task = AgentTask(
                id=str(uuid.uuid4()),
                agent_type=task_data.agent_type,
                action=task_data.action,
                parameters=task_data.parameters,
                priority=task_data.priority,
                created_at=datetime.now(),
            )

            orchestrator.submit_task(task)
            logger.info(f"Task {task.id} submitted via API")

            return {"success": True, "data": task}
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            raise HTTPException(status_code=500, detail="Failed to submit task")

    @router.get("/queue", response_model=dict)
    async def get_queue_status() -> dict:
        """Get task queue status"""
        try:
            queue_status = orchestrator.get_queue_status()
            return {"success": True, "data": queue_status}
        except Exception as e:
            logger.error(f"Error fetching queue status: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch queue status")

    return router
