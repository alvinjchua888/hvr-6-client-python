# Quick Start Guide - HVR 6.0 Python Client

Get up and running with the HVR 6.0 Python Client in minutes!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/alvinjchua888/hvr-6-client-python.git
cd hvr-6-client-python
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work for standalone mode):

```env
HVR_API_BASE_URL=http://localhost:4340
HVR_API_USERNAME=admin
HVR_API_PASSWORD=changeme
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
ENVIRONMENT=development
```

### 5. Run the Server

```bash
python -m src.server.main
```

The server will start on http://localhost:3000

## Verify Installation

### Check Server is Running

```bash
curl http://localhost:3000/
```

Expected response:
```json
{
  "name": "HVR 6.0 Client Agents API",
  "version": "1.0.0",
  "status": "running"
}
```

### View API Documentation

Open your browser and visit:
- **Interactive API Docs**: http://localhost:3000/docs
- **Alternative Docs**: http://localhost:3000/redoc

### List All Agents

```bash
curl http://localhost:3000/api/agents/
```

You should see 6 agents:
- Refresh Agent
- CDC Agent
- Integration Agent
- Compare Agent
- Monitor Agent
- Schedule Agent

## Your First Task

### Submit a Refresh Task

```bash
curl -X POST http://localhost:3000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "agentType": "REFRESH",
    "action": "refresh",
    "parameters": {
      "channelId": "my-first-channel",
      "tables": [
        {
          "sourceSchema": "SAP",
          "sourceTable": "MARA",
          "targetSchema": "WAREHOUSE",
          "targetTable": "MARA"
        }
      ],
      "estimatedRows": 10000
    },
    "priority": 5
  }'
```

### Check Job Status

```bash
curl http://localhost:3000/api/jobs/
```

You'll see your job with:
- Job ID
- Status (RUNNING or COMPLETED)
- Progress (0-100%)
- Detailed logs

## WebSocket Real-Time Updates

Connect to WebSocket for live updates:

```javascript
const ws = new WebSocket('ws://localhost:3000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type);
  console.log('Data:', data.data);
};
```

Events you'll receive:
- `taskStarted` - When a task begins execution
- `taskCompleted` - When a task completes successfully
- `taskFailed` - If a task fails

## Running with Docker

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Using Docker Directly

```bash
# Build image
docker build -t hvr6-client-python .

# Run container
docker run -p 3000:3000 hvr6-client-python
```

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Development Mode

For development with auto-reload:

```bash
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 3000
```

Or:

```bash
python -m src.server.main
# (auto-reload is enabled when ENVIRONMENT=development)
```

## Common Commands

### Check System Health

```bash
curl http://localhost:3000/api/health/
```

### View Task Queue

```bash
curl http://localhost:3000/api/tasks/queue
```

### Get Specific Agent

```bash
curl http://localhost:3000/api/agents/type/REFRESH
```

### Get Specific Job

```bash
curl http://localhost:3000/api/jobs/{job-id}
```

## Next Steps

1. **Explore the API** - Visit http://localhost:3000/docs
2. **Read the README** - See [README.md](./README.md) for detailed information
3. **HVR Integration** - See [HVR_INTEGRATION.md](./HVR_INTEGRATION.md) to connect to real HVR 6.0
4. **Submit Different Tasks** - Try CDC, Integration, Compare, Monitor, and Schedule agents
5. **Monitor with WebSocket** - Build a real-time dashboard

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:

```bash
# Change port in .env
PORT=8000

# Or specify when running
PORT=8000 python -m src.server.main
```

### Import Errors

Make sure you're in the project root directory and virtual environment is activated:

```bash
# Check current directory
pwd  # Should end with hvr-6-client-python

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Dependencies Not Found

Reinstall dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Getting Help

- **Documentation**: Check [README.md](./README.md)
- **API Issues**: Visit http://localhost:3000/docs
- **HVR Integration**: See [HVR_INTEGRATION.md](./HVR_INTEGRATION.md)
- **Conversion Info**: See [CONVERSION_NOTES.md](./CONVERSION_NOTES.md)
- **GitHub Issues**: Open an issue on the repository

## Quick Reference Card

```bash
# Start server
python -m src.server.main

# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# View logs
tail -f logs/combined.log

# Docker start
docker-compose up -d

# Docker stop
docker-compose down

# Docker logs
docker-compose logs -f
```

## What's Next?

✅ Server is running
✅ Agents are initialized
✅ API is ready
✅ WebSocket is available

Now you can:
- Submit tasks via REST API
- Monitor jobs in real-time
- Integrate with HVR 6.0
- Build custom workflows
- Create dashboards

Happy coding! 🚀
