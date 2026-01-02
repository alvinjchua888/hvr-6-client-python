"""
Base Agent class

All specialized agents extend this base class.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.shared.types import Agent, AgentMetrics, AgentStatus, AgentTask, AgentType, Job, JobStatus
from src.server.utils.logger import get_logger

logger = get_logger("base_agent")


class BaseAgent(ABC):
    """
    Base Agent class that all specialized agents extend

    Provides common functionality for task execution, metrics collection,
    and status management.
    """

    def __init__(self, agent_type: AgentType, name: str, capabilities: List[str]):
        """
        Initialize base agent

        Args:
            agent_type: Type of the agent
            name: Human-readable name
            capabilities: List of capabilities this agent has
        """
        self.id = str(uuid.uuid4())
        self.type = agent_type
        self.name = name
        self.status = AgentStatus.IDLE
        self.capabilities = capabilities
        self.last_heartbeat = datetime.now()
        self.current_job: Optional[str] = None

        # Metrics
        self.metrics = AgentMetrics(
            tasks_completed=0,
            tasks_failed=0,
            average_execution_time=0.0,
            last_execution_time=None,
            throughput=None,
        )

        self._execution_times: List[float] = []

    async def execute_task(self, task: AgentTask) -> Job:
        """
        Execute a task assigned to this agent

        Args:
            task: The task to execute

        Returns:
            Job object with execution results
        """
        logger.info(f"Agent {self.name} ({self.id}) starting task {task.id}")

        # Create job
        job = Job(
            id=str(uuid.uuid4()),
            channel_id=task.parameters.get("channelId", ""),
            agent_id=self.id,
            agent_type=self.type,
            status=JobStatus.RUNNING,
            start_time=datetime.now(),
            progress=0,
            records_processed=0,
            records_failed=0,
            logs=[],
        )

        self.current_job = job.id
        self.status = AgentStatus.RUNNING

        try:
            start_time = datetime.now()
            await self.perform_task(task, job)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000  # milliseconds

            # Update execution times
            self._execution_times.append(execution_time)
            if len(self._execution_times) > 100:
                self._execution_times.pop(0)

            # Update metrics
            self.metrics.tasks_completed += 1
            self.metrics.last_execution_time = execution_time
            self.metrics.average_execution_time = sum(self._execution_times) / len(
                self._execution_times
            )

            # Update job
            job.status = JobStatus.COMPLETED
            job.end_time = datetime.now()
            job.progress = 100

            logger.info(f"Agent {self.name} completed task {task.id} in {execution_time}ms")

        except Exception as error:
            self.metrics.tasks_failed += 1
            job.status = JobStatus.FAILED
            job.end_time = datetime.now()
            job.error_message = str(error)

            logger.error(f"Agent {self.name} failed task {task.id}: {job.error_message}")

        finally:
            self.current_job = None
            self.status = AgentStatus.IDLE
            self.update_heartbeat()

        return job

    @abstractmethod
    async def perform_task(self, task: AgentTask, job: Job) -> None:
        """
        Abstract method that specialized agents must implement

        Args:
            task: The task to perform
            job: The job object to update with progress and logs
        """
        pass

    def update_heartbeat(self) -> None:
        """Update the last heartbeat timestamp"""
        self.last_heartbeat = datetime.now()

    def pause(self) -> None:
        """Pause the agent"""
        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.PAUSED
            logger.info(f"Agent {self.name} paused")

    def resume(self) -> None:
        """Resume the agent"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.IDLE
            logger.info(f"Agent {self.name} resumed")

    def get_info(self) -> Agent:
        """
        Get agent information

        Returns:
            Agent object with current state
        """
        return Agent(
            id=self.id,
            type=self.type,
            name=self.name,
            status=self.status,
            current_job=self.current_job,
            capabilities=self.capabilities,
            last_heartbeat=self.last_heartbeat,
            metrics=self.metrics,
        )
