"""
Refresh Agent

Handles initial data load operations from SAP source to target.
"""

import asyncio
from datetime import datetime

from src.shared.types import AgentTask, AgentType, Job, LogEntry, LogLevel
from src.server.agents.base_agent import BaseAgent
from src.server.utils.logger import get_logger

logger = get_logger("refresh_agent")


class RefreshAgent(BaseAgent):
    """
    Refresh Agent - Handles initial data load operations

    Performs bulk data loading from SAP source to target with features like:
    - Table slicing for parallel processing
    - Progress tracking
    - High-performance initial loads
    """

    def __init__(self):
        super().__init__(
            agent_type=AgentType.REFRESH,
            name="Refresh Agent",
            capabilities=["initial_load", "bulk_copy", "table_slicing", "parallel_load"],
        )

    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Perform initial data load task

        Args:
            task: Task containing table mappings and parameters
            job: Job object to update with progress
        """
        logger.info(f"RefreshAgent: Starting initial data load for channel {task.parameters.get('channelId')}")

        tables = task.parameters.get("tables", [])
        total_tables = len(tables)
        processed_tables = 0

        for table in tables:
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message=f"Starting refresh for table {table.get('sourceSchema')}.{table.get('sourceTable')}",
                metadata={"table": table},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)

            # Simulate table refresh operation
            await self._refresh_table(table, job)

            processed_tables += 1
            job.progress = round((processed_tables / total_tables) * 100)

            logger.info(
                f"RefreshAgent: Refreshed table {table.get('sourceTable')} ({processed_tables}/{total_tables})"
            )

        job.records_processed = task.parameters.get("estimatedRows", 0)
        logger.info(f"RefreshAgent: Completed initial load of {total_tables} tables")

    async def _refresh_table(self, table: dict, job: Job) -> None:
        """
        Refresh a single table with parallel slicing

        Args:
            table: Table mapping configuration
            job: Job object to update with logs
        """
        # Simulate refresh operation with table slicing for parallel processing
        slices = 4  # Number of parallel slices

        for i in range(slices):
            # Simulate slice processing
            await asyncio.sleep(0.1)

            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.DEBUG,
                message=f"Processed slice {i + 1}/{slices} for table {table.get('sourceTable')}",
                metadata={"slice": i + 1, "total": slices},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)
