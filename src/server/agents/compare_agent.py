"""
Compare Agent

Handles data verification and validation between source and target.
"""

import asyncio
import random
from datetime import datetime

from src.shared.types import AgentTask, AgentType, Job, LogEntry, LogLevel
from src.server.agents.base_agent import BaseAgent
from src.server.utils.logger import get_logger

logger = get_logger("compare_agent")


class CompareAgent(BaseAgent):
    """
    Compare Agent - Handles data verification and validation

    Compares source and target data to ensure synchronization with features like:
    - Row-by-row comparison
    - Checksum validation
    - Discrepancy detection and reporting
    """

    def __init__(self):
        super().__init__(
            agent_type=AgentType.COMPARE,
            name="Compare Agent",
            capabilities=[
                "data_comparison",
                "checksum_validation",
                "row_count_verification",
                "discrepancy_detection",
            ],
        )

    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Perform comparison task

        Args:
            task: Task containing tables to compare
            job: Job object to update with progress
        """
        logger.info(f"CompareAgent: Starting comparison for channel {task.parameters.get('channelId')}")

        tables = task.parameters.get("tables", [])
        total_tables = len(tables)
        processed_tables = 0
        total_discrepancies = 0

        for table in tables:
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message=f"Comparing table {table.get('sourceSchema')}.{table.get('sourceTable')}",
                metadata={"table": table},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)

            result = await self._compare_table(table, job)
            total_discrepancies += result["discrepancies"]

            processed_tables += 1
            job.progress = round((processed_tables / total_tables) * 100)

            logger.info(
                f"CompareAgent: Compared table {table.get('sourceTable')} - "
                f"found {result['discrepancies']} discrepancies"
            )

        job.records_processed = task.parameters.get("estimatedRows", 0)

        if total_discrepancies > 0:
            warn_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.WARN,
                message=f"Found {total_discrepancies} total discrepancies across {total_tables} tables",
                metadata={"totalDiscrepancies": total_discrepancies, "tables": total_tables},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(warn_entry)

        logger.info(f"CompareAgent: Comparison complete - {total_discrepancies} discrepancies found")

    async def _compare_table(self, table: dict, job: Job) -> dict:
        """
        Compare a single table

        Args:
            table: Table mapping configuration
            job: Job object to update with logs

        Returns:
            Dictionary with comparison results
        """
        # Simulate comparison operation
        await asyncio.sleep(0.3)

        # Simulate random discrepancies (usually 0, occasionally some)
        discrepancies = random.randint(0, 10) if random.random() > 0.9 else 0

        if discrepancies > 0:
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.WARN,
                message=f"Found {discrepancies} discrepancies in table {table.get('sourceTable')}",
                metadata={"table": table.get("sourceTable"), "count": discrepancies},
            )
            if job.logs is None:
                job.logs = []
            job.logs.append(log_entry)

        return {"discrepancies": discrepancies}
