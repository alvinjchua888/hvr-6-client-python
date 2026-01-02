"""
Tests for agent implementations
"""

import pytest

from src.shared.types import AgentTask, AgentType
from src.server.agents.refresh_agent import RefreshAgent


@pytest.mark.asyncio
async def test_refresh_agent_creation():
    """Test that RefreshAgent can be created"""
    agent = RefreshAgent()
    
    assert agent.type == AgentType.REFRESH
    assert agent.name == "Refresh Agent"
    assert "initial_load" in agent.capabilities
    assert "bulk_copy" in agent.capabilities


@pytest.mark.asyncio
async def test_refresh_agent_execute_task():
    """Test that RefreshAgent can execute a task"""
    agent = RefreshAgent()
    
    task = AgentTask(
        id="test-task-1",
        agent_type=AgentType.REFRESH,
        action="refresh",
        parameters={
            "channelId": "test-channel",
            "tables": [
                {
                    "sourceSchema": "SAP",
                    "sourceTable": "MARA",
                    "targetSchema": "WAREHOUSE",
                    "targetTable": "MARA"
                }
            ],
            "estimatedRows": 1000
        },
        priority=5,
        created_at="2024-01-01T00:00:00"
    )
    
    job = await agent.execute_task(task)
    
    assert job.id is not None
    assert job.agent_id == agent.id
    assert job.progress == 100
    assert job.records_processed == 1000
