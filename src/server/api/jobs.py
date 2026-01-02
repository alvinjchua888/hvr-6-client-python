"""
Jobs API endpoints
"""

from fastapi import APIRouter, HTTPException

from src.server.agents.agent_orchestrator import AgentOrchestrator
from src.server.utils.logger import get_logger

logger = get_logger("api.jobs")


def create_jobs_router(orchestrator: AgentOrchestrator) -> APIRouter:
    """
    Create jobs API router

    Args:
        orchestrator: Agent orchestrator instance

    Returns:
        Configured router
    """
    router = APIRouter(prefix="/api/jobs", tags=["jobs"])

    @router.get("/", response_model=dict)
    async def get_all_jobs() -> dict:
        """Get all active jobs"""
        try:
            jobs = orchestrator.get_active_jobs()
            return {"success": True, "data": jobs}
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch jobs")

    @router.get("/{job_id}", response_model=dict)
    async def get_job(job_id: str) -> dict:
        """Get job by ID"""
        try:
            job = orchestrator.get_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return {"success": True, "data": job}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching job: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch job")

    return router
