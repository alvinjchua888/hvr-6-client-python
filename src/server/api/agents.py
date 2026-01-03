"""
Agents API endpoints
"""

from typing import List

from fastapi import APIRouter, HTTPException

from src.server.agents.agent_orchestrator import AgentOrchestrator
from src.server.utils.logger import get_logger
from src.shared.types import Agent, AgentType

logger = get_logger("api.agents")


def create_agents_router(orchestrator: AgentOrchestrator) -> APIRouter:
    """
    Create agents API router

    Args:
        orchestrator: Agent orchestrator instance

    Returns:
        Configured router
    """
    router = APIRouter(prefix="/api/agents", tags=["agents"])

    @router.get("/", response_model=dict)
    async def get_all_agents() -> dict:
        """Get all agents"""
        try:
            agents = orchestrator.get_all_agents()
            return {"success": True, "data": agents}
        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch agents")

    @router.get("/{agent_id}", response_model=dict)
    async def get_agent(agent_id: str) -> dict:
        """Get agent by ID"""
        try:
            agent = orchestrator.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            return {"success": True, "data": agent}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching agent: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch agent")

    @router.get("/type/{agent_type}", response_model=dict)
    async def get_agents_by_type(agent_type: str) -> dict:
        """Get agents by type"""
        try:
            # Validate agent type
            try:
                agent_type_enum = AgentType(agent_type.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid agent type")

            agents = orchestrator.get_agents_by_type(agent_type_enum)
            return {"success": True, "data": agents}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching agents by type: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch agents")

    return router
