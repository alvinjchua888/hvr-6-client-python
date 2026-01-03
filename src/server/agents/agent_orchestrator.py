"""
Agent Orchestrator

Central coordinator for all agents that manages agent lifecycle,
task distribution, and coordination.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from src.shared.types import Agent, AgentStatus, AgentTask, AgentType, Job
from src.server.agents.base_agent import BaseAgent
from src.server.agents.cdc_agent import CDCAgent
from src.server.agents.compare_agent import CompareAgent
from src.server.agents.integration_agent import IntegrationAgent
from src.server.agents.monitor_agent import MonitorAgent
from src.server.agents.refresh_agent import RefreshAgent
from src.server.agents.schedule_agent import ScheduleAgent
from src.server.utils.logger import get_logger

logger = get_logger("orchestrator")


class AgentOrchestrator:
    """
    AgentOrchestrator - Central coordinator for all agents

    Manages:
    - Agent lifecycle
    - Task distribution
    - Agent coordination
    - Task queuing and prioritization
    """

    def __init__(self):
        """Initialize the orchestrator"""
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.active_jobs: Dict[str, Job] = {}
        self.is_running = False
        self._process_task: Optional[asyncio.Task] = None
        self._event_callbacks: Dict[str, List[callable]] = {
            "started": [],
            "stopped": [],
            "taskSubmitted": [],
            "taskStarted": [],
            "taskCompleted": [],
            "taskFailed": [],
        }

        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all agent types"""
        agent_instances = [
            RefreshAgent(),
            CDCAgent(),
            IntegrationAgent(),
            CompareAgent(),
            MonitorAgent(),
            ScheduleAgent(),
        ]

        for agent in agent_instances:
            self.agents[agent.id] = agent
            logger.info(f"Initialized agent: {agent.name} ({agent.id})")

    def start(self) -> None:
        """Start the orchestrator"""
        if self.is_running:
            logger.warning("AgentOrchestrator already running")
            return

        self.is_running = True
        logger.info("AgentOrchestrator started")
        self._emit("started", {})

        # Start processing task queue in background
        self._process_task = asyncio.create_task(self._process_task_queue())

    def stop(self) -> None:
        """Stop the orchestrator"""
        self.is_running = False
        if self._process_task:
            self._process_task.cancel()
        logger.info("AgentOrchestrator stopped")
        self._emit("stopped", {})

    def submit_task(self, task: AgentTask) -> None:
        """
        Submit a task to the queue

        Args:
            task: The task to submit
        """
        self.task_queue.append(task)
        logger.info(f"Task {task.id} submitted to queue")
        self._emit("taskSubmitted", task)

    async def _process_task_queue(self) -> None:
        """Process tasks in the queue"""
        while self.is_running:
            if len(self.task_queue) > 0:
                # Sort by priority (higher first)
                self.task_queue.sort(key=lambda t: t.priority, reverse=True)

                # Find an available agent for the next task
                task = self.task_queue[0]
                agent = self._find_available_agent(task.agent_type)

                if agent:
                    self.task_queue.pop(0)
                    # Execute task in background
                    asyncio.create_task(self._execute_task(agent, task))
                else:
                    # No available agent, wait and retry
                    await asyncio.sleep(1)
            else:
                # No tasks in queue, wait
                await asyncio.sleep(1)

    def _find_available_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """
        Find an available agent of the specified type

        Args:
            agent_type: Type of agent to find

        Returns:
            Available agent or None
        """
        for agent in self.agents.values():
            if agent.type == agent_type and agent.status == AgentStatus.IDLE:
                return agent
        return None

    async def _execute_task(self, agent: BaseAgent, task: AgentTask) -> None:
        """
        Execute a task on an agent

        Args:
            agent: The agent to execute the task
            task: The task to execute
        """
        logger.info(f"Assigning task {task.id} to agent {agent.name}")
        self._emit("taskStarted", {"agent": agent.get_info(), "task": task})

        try:
            job = await agent.execute_task(task)
            self.active_jobs[job.id] = job
            self._emit("taskCompleted", {"agent": agent.get_info(), "task": task, "job": job})
            logger.info(f"Task {task.id} completed by agent {agent.name}")
        except Exception as error:
            self._emit("taskFailed", {"agent": agent.get_info(), "task": task, "error": str(error)})
            logger.error(f"Task {task.id} failed on agent {agent.name}: {error}")

    def get_all_agents(self) -> List[Agent]:
        """
        Get all agents

        Returns:
            List of all agents
        """
        return [agent.get_info() for agent in self.agents.values()]

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID

        Args:
            agent_id: Agent ID

        Returns:
            Agent or None
        """
        agent = self.agents.get(agent_id)
        return agent.get_info() if agent else None

    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """
        Get agents by type

        Args:
            agent_type: Agent type

        Returns:
            List of agents of the specified type
        """
        return [
            agent.get_info() for agent in self.agents.values() if agent.type == agent_type
        ]

    def get_active_jobs(self) -> List[Job]:
        """
        Get all active jobs

        Returns:
            List of active jobs
        """
        return list(self.active_jobs.values())

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID

        Args:
            job_id: Job ID

        Returns:
            Job or None
        """
        return self.active_jobs.get(job_id)

    def get_queue_status(self) -> Dict:
        """
        Get task queue status

        Returns:
            Dictionary with queue information
        """
        return {"pending": len(self.task_queue), "tasks": self.task_queue}

    def cleanup_old_jobs(self, max_age: int = 3600000) -> None:
        """
        Clear completed jobs older than specified time

        Args:
            max_age: Maximum age in milliseconds
        """
        now = datetime.now()
        jobs_to_remove = []

        for job_id, job in self.active_jobs.items():
            if job.end_time:
                age = (now - job.end_time).total_seconds() * 1000
                if age > max_age:
                    jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]

        if len(jobs_to_remove) > 0:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")

    def on(self, event: str, callback: callable) -> None:
        """
        Register event callback

        Args:
            event: Event name
            callback: Callback function
        """
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)

    def _emit(self, event: str, data: any) -> None:
        """
        Emit an event to all registered callbacks

        Args:
            event: Event name
            data: Event data
        """
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback for {event}: {e}")
