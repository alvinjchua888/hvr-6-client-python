"""
Health API endpoints
"""

import os
import psutil
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.server.agents.agent_orchestrator import AgentOrchestrator
from src.server.utils.logger import get_logger
from src.shared.types import (
    AgentHealthStats,
    AgentStatus,
    ChannelHealthStats,
    JobHealthStats,
    JobStatus,
    PerformanceStats,
    SystemHealth,
)

logger = get_logger("api.health")


def create_health_router(orchestrator: AgentOrchestrator) -> APIRouter:
    """
    Create health API router

    Args:
        orchestrator: Agent orchestrator instance

    Returns:
        Configured router
    """
    router = APIRouter(prefix="/api/health", tags=["health"])

    @router.get("/", response_model=dict)
    async def get_system_health() -> dict:
        """Get system health status"""
        try:
            agents = orchestrator.get_all_agents()
            jobs = orchestrator.get_active_jobs()

            # Calculate agent statistics
            agent_stats = AgentHealthStats(
                total=len(agents),
                active=sum(1 for a in agents if a.status == AgentStatus.RUNNING),
                idle=sum(1 for a in agents if a.status == AgentStatus.IDLE),
                error=sum(1 for a in agents if a.status == AgentStatus.ERROR),
            )

            # Calculate job statistics
            job_stats = JobHealthStats(
                total=len(jobs),
                running=sum(1 for j in jobs if j.status == JobStatus.RUNNING),
                completed=sum(1 for j in jobs if j.status == JobStatus.COMPLETED),
                failed=sum(1 for j in jobs if j.status == JobStatus.FAILED),
            )

            # Channel statistics (would be populated from actual channel data)
            channel_stats = ChannelHealthStats(total=0, active=0)

            # Get system performance metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            performance_stats = PerformanceStats(
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                network_throughput=0.0,  # Would need actual network monitoring
            )

            # Create system health object
            health = SystemHealth(
                timestamp=datetime.now(),
                agents=agent_stats,
                jobs=job_stats,
                channels=channel_stats,
                performance=performance_stats,
            )

            return {"success": True, "data": health}
        except Exception as e:
            logger.error(f"Error fetching health: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch health")

    return router
