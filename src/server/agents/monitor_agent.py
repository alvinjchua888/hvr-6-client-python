"""
Monitor Agent

Handles system health monitoring and alerting.
"""

import asyncio
import random
from datetime import datetime

from src.shared.types import AgentTask, AgentType, Job, LogEntry, LogLevel
from src.server.agents.base_agent import BaseAgent
from src.server.utils.logger import get_logger

logger = get_logger("monitor_agent")


class MonitorAgent(BaseAgent):
    """
    Monitor Agent - Handles system health monitoring and alerting

    Tracks replication health, performance, and issues with features like:
    - Performance metrics tracking
    - Health checks and alerting
    - Real-time status monitoring
    """

    def __init__(self):
        super().__init__(
            agent_type=AgentType.MONITOR,
            name="Monitor Agent",
            capabilities=[
                "health_monitoring",
                "performance_tracking",
                "alerting",
                "metrics_collection",
            ],
        )

    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Perform monitoring task

        Args:
            task: Task containing monitoring parameters
            job: Job object to update with progress
        """
        logger.info(f"MonitorAgent: Starting monitoring for channel {task.parameters.get('channelId')}")

        duration = task.parameters.get("duration", 30000) / 1000  # Convert ms to seconds
        start_time = datetime.now()
        checks = 0

        while (datetime.now() - start_time).total_seconds() < duration:
            health = await self._check_health(task.parameters)
            checks += 1

            level = LogLevel.INFO if health["status"] == "healthy" else LogLevel.WARN
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=f"Health check #{checks}: {health['status']}",
                metadata=health,
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)

            elapsed = (datetime.now() - start_time).total_seconds()
            job.progress = min(round((elapsed / duration) * 100), 99)

            # Wait before next check
            await asyncio.sleep(5)

        job.records_processed = checks
        logger.info(f"MonitorAgent: Completed {checks} health checks")

    async def _check_health(self, parameters: dict) -> dict:
        """
        Perform health check

        Args:
            parameters: Monitoring parameters

        Returns:
            Health check results
        """
        # Simulate health check
        await asyncio.sleep(0.1)

        latency = random.randint(10, 110)
        throughput = random.randint(1000, 11000)
        error_rate = random.random() * 0.05

        return {
            "status": "healthy" if error_rate < 0.03 else "degraded",
            "latency": latency,
            "throughput": throughput,
            "errorRate": f"{error_rate:.4f}",
            "timestamp": datetime.now(),
        }
