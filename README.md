# hvr-6-client-python
Python based HVR 6 Client

A comprehensive multi-agent architecture for managing HVR 6.0 SAP data replication operations, written in Python with FastAPI.

## Overview

This application provides a complete solution for managing critical SAP data replication operations using Fivetran's HVR 6.0 technology. It implements a multi-agent architecture that handles all aspects of data replication from SAP systems to various target platforms.

**✅ HVR 6.0 Integration:** This system can integrate directly with Fivetran's HVR 6.0 product via REST API. It operates in two modes:
- **Standalone Mode** (Default): Demonstrates all features without requiring HVR installation
- **Integrated Mode**: Connects to actual HVR 6.0 for real production data replication

## Features

### 🤖 Multi-Agent Architecture

The system includes six specialized agents, each handling specific replication tasks:

1. **Refresh Agent** - Initial data load operations
   - Bulk data copying from SAP to target
   - Table slicing for parallel processing
   - High-performance initial loads

2. **CDC Agent** - Change Data Capture
   - Real-time transaction log monitoring
   - Log-based CDC for minimal source impact
   - Continuous change tracking

3. **Integration Agent** - Data integration to targets
   - Applies captured changes to target systems
   - Batch processing for efficiency
   - Conflict resolution

4. **Compare Agent** - Data verification
   - Source-to-target comparison
   - Discrepancy detection
   - Data validation and compliance

5. **Monitor Agent** - System health monitoring
   - Performance metrics tracking
   - Health checks and alerting
   - Real-time status monitoring

6. **Schedule Agent** - Workflow automation
   - Task scheduling and orchestration
   - Dependency management
   - Automated workflow execution

### 🎨 REST API & WebSocket

- **REST API**: Full-featured API for agent, job, and task management
- **WebSocket**: Real-time updates for connected clients
- **OpenAPI Documentation**: Auto-generated API docs at `/docs`

### 🔧 Technical Stack

- **Python 3.9+**
- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation using Python type hints
- **httpx** - Async HTTP client for HVR API integration
- **WebSockets** - Real-time bidirectional communication
- **uvicorn** - Lightning-fast ASGI server

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/alvinjchua888/hvr-6-client-python.git
cd hvr-6-client-python
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. For development, also install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your HVR 6.0 configuration:
```env
HVR_API_BASE_URL=http://localhost:4340
HVR_API_USERNAME=admin
HVR_API_PASSWORD=changeme
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
ENVIRONMENT=development
```

### Running the Application

#### Development Mode

Run the server with auto-reload:
```bash
python -m src.server.main
```

Or using uvicorn directly:
```bash
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 3000
```

The server will start on http://localhost:3000

- API Documentation: http://localhost:3000/docs
- Alternative API Docs: http://localhost:3000/redoc
- WebSocket: ws://localhost:3000/ws

#### Production Mode

Using Docker:
```bash
docker-compose up -d
```

Or run directly:
```bash
ENVIRONMENT=production python -m src.server.main
```

## HVR 6.0 Integration

### Standalone Mode (Default)

The application runs in standalone mode by default, simulating all HVR operations for demonstration and testing purposes. No HVR 6.0 installation is required.

### Integrated Mode with HVR 6.0

To connect to an actual HVR 6.0 installation:

1. **Install HVR 6.0**: Follow [Fivetran's HVR 6.0 installation guide](https://docs.fivetran.com/hvr6/getting-started)

2. **Configure connection** in `.env`:
```env
HVR_API_BASE_URL=http://your-hvr-server:4340
HVR_API_USERNAME=admin
HVR_API_PASSWORD=your-password
HVR_INTEGRATED_MODE=true  # Enable real HVR integration
```

3. **Restart the application**:
```bash
python -m src.server.main
```

The system will automatically use the HVR 6.0 REST API for all replication operations.

## API Documentation

### Agents

- `GET /api/agents` - Get all agents
- `GET /api/agents/{id}` - Get agent by ID
- `GET /api/agents/type/{type}` - Get agents by type

### Jobs

- `GET /api/jobs` - Get all active jobs
- `GET /api/jobs/{id}` - Get job by ID

### Tasks

- `POST /api/tasks` - Submit a new task
- `GET /api/tasks/queue` - Get task queue status

### Health

- `GET /api/health` - Get system health status

### Example: Submit a Refresh Task

```bash
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agentType": "REFRESH",
    "action": "refresh",
    "parameters": {
      "channelId": "sap-to-snowflake",
      "tables": [
        {
          "sourceSchema": "SAP",
          "sourceTable": "MARA",
          "targetSchema": "WAREHOUSE",
          "targetTable": "MARA"
        }
      ],
      "estimatedRows": 1000000
    },
    "priority": 5
  }'
```

## Project Structure

```
hvr-6-client-python/
├── src/
│   ├── server/
│   │   ├── agents/              # Agent implementations
│   │   │   ├── base_agent.py
│   │   │   ├── refresh_agent.py
│   │   │   ├── cdc_agent.py
│   │   │   ├── integration_agent.py
│   │   │   ├── compare_agent.py
│   │   │   ├── monitor_agent.py
│   │   │   ├── schedule_agent.py
│   │   │   └── agent_orchestrator.py
│   │   ├── api/                 # REST API routes
│   │   │   ├── agents.py
│   │   │   ├── jobs.py
│   │   │   ├── tasks.py
│   │   │   └── health.py
│   │   ├── hvr/                 # HVR client
│   │   │   └── hvr_client.py
│   │   ├── utils/               # Utilities
│   │   │   └── logger.py
│   │   └── main.py              # Server entry point
│   └── shared/
│       └── types.py             # Shared type definitions
├── tests/                       # Test files
├── logs/                        # Log files
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── pyproject.toml               # Project configuration
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md                    # This file
```

## Development

### Code Formatting

Format code with Black:
```bash
black src/ tests/
```

### Linting

Lint code with Ruff:
```bash
ruff check src/ tests/
```

### Type Checking

Run type checking with mypy:
```bash
mypy src/
```

### Running Tests

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src --cov-report=html
```

## WebSocket Integration

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:3000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // Handle different event types
  switch(data.type) {
    case 'taskStarted':
      console.log('Task started:', data.data);
      break;
    case 'taskCompleted':
      console.log('Task completed:', data.data);
      break;
    case 'taskFailed':
      console.log('Task failed:', data.data);
      break;
  }
};
```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t hvr6-client-python .

# Run container
docker run -p 3000:3000 --env-file .env hvr6-client-python
```

Or use Docker Compose:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

Built for HVR 6.0 (Fivetran Local Data Processing) to manage SAP data replication operations efficiently and securely.

This is the Python implementation of the [hvr6-client-agents](https://github.com/alvinjchua888/hvr6-client-agents) TypeScript/Node.js version.

