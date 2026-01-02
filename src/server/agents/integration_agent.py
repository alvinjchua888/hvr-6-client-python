"""
Integration Agent

Handles data integration to target systems by applying captured changes.
"""

import asyncio
import random
from datetime import datetime

from src.shared.types import AgentTask, AgentType, Job, LogEntry, LogLevel
from src.server.agents.base_agent import BaseAgent
from src.server.utils.logger import get_logger

logger = get_logger("integration_agent")


class IntegrationAgent(BaseAgent):
    """
    Integration Agent - Handles data integration to target systems

    Applies captured changes to the target database with features like:
    - Batch processing for efficiency
    - Conflict resolution
    - Transaction consistency
    """

    def __init__(self):
        super().__init__(
            agent_type=AgentType.INTEGRATE,
            name="Integration Agent",
            capabilities=[
                "apply_changes",
                "batch_processing",
                "conflict_resolution",
                "transaction_apply",
            ],
        )

    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Perform integration task

        Args:
            task: Task containing changes to apply
            job: Job object to update with progress
        """
        logger.info(f"IntegrationAgent: Starting integration for channel {task.parameters.get('channelId')}")

        changes = task.parameters.get("changes", [])
        batch_size = 100
        total_batches = (len(changes) + batch_size - 1) // batch_size
        processed_batches = 0

        for i in range(0, len(changes), batch_size):
            batch = changes[i : i + batch_size]

            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message=f"Applying batch {processed_batches + 1}/{total_batches} ({len(batch)} changes)",
                metadata={"batchNumber": processed_batches + 1, "batchSize": len(batch)},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)

            await self._apply_batch(batch, job)

            processed_batches += 1
            job.progress = round((processed_batches / total_batches) * 100)
            job.records_processed = (job.records_processed or 0) + len(batch)

        logger.info(f"IntegrationAgent: Applied {len(changes)} changes to target")

    async def _apply_batch(self, batch: list, job: Job) -> None:
        """
        Apply a batch of changes to target system

        Args:
            batch: List of changes to apply
            job: Job object to update with logs
        """
        # Simulate applying changes to target system
        await asyncio.sleep(0.2)

        # Simulate some failures (1% failure rate)
        failed_changes = int(random.random() * len(batch) * 0.01)
        if failed_changes > 0:
            job.records_failed = (job.records_failed or 0) + failed_changes

            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.WARN,
                message=f"{failed_changes} changes failed to apply",
                metadata={"failures": failed_changes},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)
