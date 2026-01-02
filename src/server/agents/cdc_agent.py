"""
CDC Agent

Handles Change Data Capture operations by monitoring transaction logs.
"""

import asyncio
import random
from datetime import datetime

from src.shared.types import AgentTask, AgentType, Job, LogEntry, LogLevel
from src.server.agents.base_agent import BaseAgent
from src.server.utils.logger import get_logger

logger = get_logger("cdc_agent")


class CDCAgent(BaseAgent):
    """
    CDC Agent - Handles Change Data Capture operations

    Monitors transaction logs and captures changes in real-time with features like:
    - Log-based CDC for minimal source impact
    - Real-time transaction log monitoring
    - Continuous change tracking
    """

    def __init__(self):
        super().__init__(
            agent_type=AgentType.CDC,
            name="CDC Agent",
            capabilities=[
                "log_based_cdc",
                "real_time_capture",
                "transaction_log_reading",
                "change_tracking",
            ],
        )

    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Perform CDC capture task

        Args:
            task: Task containing capture parameters
            job: Job object to update with progress
        """
        logger.info(f"CDCAgent: Starting CDC capture for channel {task.parameters.get('channelId')}")

        duration = task.parameters.get("duration", 60000) / 1000  # Convert ms to seconds
        start_time = datetime.now()
        captured_changes = 0

        # Simulate continuous CDC capture
        while (datetime.now() - start_time).total_seconds() < duration:
            changes = await self._capture_changes(task.parameters)
            captured_changes += len(changes)

            if len(changes) > 0:
                log_entry = LogEntry(
                    timestamp=datetime.now(),
                    level=LogLevel.INFO,
                    message=f"Captured {len(changes)} changes",
                    metadata={"changes": len(changes), "totalCaptured": captured_changes},
                )
                if job.logs is None:
                    job.logs = []
                job.logs.append(log_entry)

            elapsed = (datetime.now() - start_time).total_seconds()
            job.progress = min(round((elapsed / duration) * 100), 99)
            job.records_processed = captured_changes

            # Wait before next capture cycle
            await asyncio.sleep(1)

        job.records_processed = captured_changes
        logger.info(f"CDCAgent: Captured total of {captured_changes} changes")

    async def _capture_changes(self, parameters: dict) -> list:
        """
        Simulate capturing changes from transaction log

        Args:
            parameters: Capture parameters

        Returns:
            List of captured changes
        """
        # Simulate capturing changes
        change_count = random.randint(0, 50)
        changes = []

        tables = parameters.get("tables", [])
        table_name = tables[0].get("sourceTable") if tables else "SAMPLE_TABLE"

        for _ in range(change_count):
            changes.append(
                {
                    "operation": random.choice(["INSERT", "UPDATE", "DELETE"]),
                    "table": table_name,
                    "timestamp": datetime.now(),
                    "data": {},
                }
            )

        return changes
