"""
Shared types and models for HVR 6.0 Multi-Agent System

This module defines all the data models, enums, and types used across the application.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system"""

    REFRESH = "REFRESH"
    CDC = "CDC"
    INTEGRATE = "INTEGRATE"
    COMPARE = "COMPARE"
    MONITOR = "MONITOR"
    SCHEDULE = "SCHEDULE"


class AgentStatus(str, Enum):
    """Status of an agent"""

    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"


class JobStatus(str, Enum):
    """Status of a job"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReplicationMode(str, Enum):
    """Replication modes"""

    INITIAL_LOAD = "INITIAL_LOAD"
    CONTINUOUS_CDC = "CONTINUOUS_CDC"
    REFRESH_AND_CDC = "REFRESH_AND_CDC"
    COMPARE_ONLY = "COMPARE_ONLY"


class DatabaseType(str, Enum):
    """SAP database types"""

    HANA = "HANA"
    ORACLE = "ORACLE"
    DB2 = "DB2"
    MAXDB = "MAXDB"


class TargetType(str, Enum):
    """Target system types"""

    SNOWFLAKE = "SNOWFLAKE"
    REDSHIFT = "REDSHIFT"
    BIGQUERY = "BIGQUERY"
    DATABRICKS = "DATABRICKS"
    S3 = "S3"
    AZURE_BLOB = "AZURE_BLOB"


class LogLevel(str, Enum):
    """Log levels"""

    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class DiscrepancyType(str, Enum):
    """Types of data discrepancies"""

    MISMATCH = "MISMATCH"
    MISSING_SOURCE = "MISSING_SOURCE"
    MISSING_TARGET = "MISSING_TARGET"


# Data Models


class SAPConnection(BaseModel):
    """SAP source connection details"""

    id: str
    name: str
    host: str
    port: int
    system_id: str = Field(alias="systemId")
    client: str
    username: str
    password: Optional[str] = None
    database_type: DatabaseType = Field(alias="databaseType")
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class TargetConnection(BaseModel):
    """Target connection details"""

    id: str
    name: str
    type: TargetType
    connection_string: str = Field(alias="connectionString")
    credentials: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class ColumnMapping(BaseModel):
    """Column mapping configuration"""

    source_column: str = Field(alias="sourceColumn")
    target_column: str = Field(alias="targetColumn")
    transformation: Optional[str] = None

    class Config:
        populate_by_name = True


class TableMapping(BaseModel):
    """Table mapping configuration"""

    source_schema: str = Field(alias="sourceSchema")
    source_table: str = Field(alias="sourceTable")
    target_schema: str = Field(alias="targetSchema")
    target_table: str = Field(alias="targetTable")
    column_mappings: Optional[List[ColumnMapping]] = Field(default=None, alias="columnMappings")
    filters: Optional[str] = None

    class Config:
        populate_by_name = True


class ReplicationChannel(BaseModel):
    """Replication channel configuration"""

    id: str
    name: str
    source_connection: str = Field(alias="sourceConnection")
    target_connection: str = Field(alias="targetConnection")
    tables: List[TableMapping]
    mode: ReplicationMode
    status: JobStatus
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class AgentMetrics(BaseModel):
    """Agent performance metrics"""

    tasks_completed: int = Field(default=0, alias="tasksCompleted")
    tasks_failed: int = Field(default=0, alias="tasksFailed")
    average_execution_time: float = Field(default=0.0, alias="averageExecutionTime")
    last_execution_time: Optional[float] = Field(default=None, alias="lastExecutionTime")
    throughput: Optional[float] = None

    class Config:
        populate_by_name = True


class Agent(BaseModel):
    """Agent information"""

    id: str
    type: AgentType
    name: str
    status: AgentStatus
    current_job: Optional[str] = Field(default=None, alias="currentJob")
    capabilities: List[str]
    last_heartbeat: datetime = Field(alias="lastHeartbeat")
    metrics: Optional[AgentMetrics] = None

    class Config:
        populate_by_name = True


class LogEntry(BaseModel):
    """Log entry"""

    timestamp: datetime
    level: LogLevel
    message: str
    metadata: Optional[Dict[str, Any]] = None


class Job(BaseModel):
    """Job information"""

    id: str
    channel_id: str = Field(alias="channelId")
    agent_id: str = Field(alias="agentId")
    agent_type: AgentType = Field(alias="agentType")
    status: JobStatus
    start_time: Optional[datetime] = Field(default=None, alias="startTime")
    end_time: Optional[datetime] = Field(default=None, alias="endTime")
    progress: int = 0
    records_processed: Optional[int] = Field(default=0, alias="recordsProcessed")
    records_failed: Optional[int] = Field(default=0, alias="recordsFailed")
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    logs: Optional[List[LogEntry]] = None

    class Config:
        populate_by_name = True


class Discrepancy(BaseModel):
    """Data discrepancy details"""

    table: str
    row_identifier: str = Field(alias="rowIdentifier")
    column: str
    source_value: Any = Field(alias="sourceValue")
    target_value: Any = Field(alias="targetValue")
    type: DiscrepancyType

    class Config:
        populate_by_name = True


class ComparisonSummary(BaseModel):
    """Comparison summary statistics"""

    matched_rows: int = Field(alias="matchedRows")
    mismatched_rows: int = Field(alias="mismatchedRows")
    missing_in_source: int = Field(alias="missingInSource")
    missing_in_target: int = Field(alias="missingInTarget")

    class Config:
        populate_by_name = True


class ComparisonResult(BaseModel):
    """Comparison result"""

    id: str
    channel_id: str = Field(alias="channelId")
    timestamp: datetime
    tables_compared: int = Field(alias="tablesCompared")
    rows_compared: int = Field(alias="rowsCompared")
    discrepancies: List[Discrepancy]
    summary: ComparisonSummary

    class Config:
        populate_by_name = True


class AgentTask(BaseModel):
    """Agent task definition"""

    id: str
    agent_type: AgentType = Field(alias="agentType")
    action: str
    parameters: Dict[str, Any]
    priority: int = 5
    created_at: datetime = Field(alias="createdAt")
    scheduled_for: Optional[datetime] = Field(default=None, alias="scheduledFor")

    class Config:
        populate_by_name = True


class AgentHealthStats(BaseModel):
    """Agent health statistics"""

    total: int
    active: int
    idle: int
    error: int


class JobHealthStats(BaseModel):
    """Job health statistics"""

    total: int
    running: int
    completed: int
    failed: int


class ChannelHealthStats(BaseModel):
    """Channel health statistics"""

    total: int
    active: int


class PerformanceStats(BaseModel):
    """System performance statistics"""

    cpu_usage: float = Field(alias="cpuUsage")
    memory_usage: float = Field(alias="memoryUsage")
    network_throughput: float = Field(alias="networkThroughput")

    class Config:
        populate_by_name = True


class SystemHealth(BaseModel):
    """System health status"""

    timestamp: datetime
    agents: AgentHealthStats
    jobs: JobHealthStats
    channels: ChannelHealthStats
    performance: PerformanceStats
