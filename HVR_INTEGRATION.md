# HVR 6.0 Integration Guide for Python Client

This document explains how to integrate the HVR 6.0 Python Client with Fivetran's HVR 6.0 product.

## Overview

The Python HVR 6.0 Client can operate in two modes:

1. **Standalone Mode** (Default) - Simulates HVR operations for testing and demonstration
2. **Integrated Mode** - Connects to actual HVR 6.0 for production data replication

## Prerequisites for HVR Integration

- HVR 6.0 installed and running
- HVR REST API accessible
- Valid HVR credentials (username/password)
- Network connectivity to HVR server

## Configuration

### Environment Variables

Edit `.env` file with your HVR configuration:

```env
# HVR 6.0 Configuration
HVR_API_BASE_URL=http://your-hvr-server:4340
HVR_API_USERNAME=admin
HVR_API_PASSWORD=your-secure-password
HVR_INTEGRATED_MODE=true

# Server Configuration
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
ENVIRONMENT=production
```

### HVR API Endpoints Used

The client interacts with the following HVR REST API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/channels` | GET | List replication channels |
| `/api/channels/{name}` | GET | Get channel details |
| `/api/channels/{name}/stats` | GET | Get channel statistics |
| `/api/jobs/refresh` | POST | Start initial load |
| `/api/jobs/capture` | POST | Start CDC |
| `/api/jobs/integrate` | POST | Start integration |
| `/api/jobs/compare` | POST | Start comparison |
| `/api/jobs/{id}` | GET | Get job status |
| `/api/jobs/{id}/logs` | GET | Get job logs |
| `/api/jobs/{id}/stop` | POST | Stop a job |
| `/api/locations` | GET | List locations |
| `/api/locations/{name}/test` | POST | Test location |

## Agent Integration

Each agent uses the HVR API client for different operations:

### Refresh Agent → HVR Refresh API

```python
from src.server.hvr import get_hvr_client

hvr = get_hvr_client()
result = await hvr.start_refresh(
    channel_name='sap-to-snowflake',
    tables=['MARA', 'MAKT']
)
```

### CDC Agent → HVR Capture API

```python
result = await hvr.start_capture(channel_name='sap-to-snowflake')
```

### Integration Agent → HVR Integrate API

```python
result = await hvr.start_integrate(channel_name='sap-to-snowflake')
```

### Compare Agent → HVR Compare API

```python
result = await hvr.start_compare(
    channel_name='sap-to-snowflake',
    tables=['MARA', 'MAKT']
)
```

## Testing HVR Connection

### 1. Using Python Code

```python
import asyncio
from src.server.hvr import get_hvr_client

async def test_hvr():
    hvr = get_hvr_client()
    is_healthy = await hvr.health_check()
    
    if is_healthy:
        print("✅ HVR connection successful")
        channels = await hvr.list_channels()
        print(f"Found {len(channels)} channels")
    else:
        print("❌ HVR connection failed")

asyncio.run(test_hvr())
```

### 2. Using API Endpoint

```bash
# Start the server
python -m src.server.main

# In another terminal, test the health endpoint
curl http://localhost:3000/api/health/ | python -m json.tool
```

### 3. Using HVR REST API Directly

```bash
curl -u admin:password http://hvr-server:4340/api/health
```

## Example: Complete Replication Workflow

### 1. Create a Refresh Task

```bash
curl -X POST http://localhost:3000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "agentType": "REFRESH",
    "action": "refresh",
    "parameters": {
      "channelId": "sap-to-snowflake",
      "tables": [
        {
          "sourceSchema": "SAPABAP1",
          "sourceTable": "MARA",
          "targetSchema": "SAP_DATA",
          "targetTable": "MARA"
        }
      ],
      "estimatedRows": 1000000
    },
    "priority": 10
  }'
```

### 2. Monitor Job Progress

```bash
# Get all jobs
curl http://localhost:3000/api/jobs/

# Get specific job
curl http://localhost:3000/api/jobs/{job-id}
```

### 3. Start CDC

```bash
curl -X POST http://localhost:3000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "agentType": "CDC",
    "action": "capture",
    "parameters": {
      "channelId": "sap-to-snowflake",
      "duration": 3600000
    },
    "priority": 8
  }'
```

## Troubleshooting

### Connection Refused

**Problem:** Cannot connect to HVR API

**Solution:**
1. Check HVR server is running: `curl http://hvr-server:4340/api/health`
2. Verify firewall rules allow port 4340
3. Check HVR_API_BASE_URL in .env

### Authentication Failed

**Problem:** 401 Unauthorized errors

**Solution:**
1. Verify credentials in .env
2. Check HVR user permissions
3. Test credentials: `curl -u username:password http://hvr-server:4340/api/channels`

### Timeout Errors

**Problem:** Requests timing out

**Solution:**
1. Increase timeout in hvr_client.py
2. Check network latency
3. Verify HVR server resources

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t hvr6-client-python .

# Run with HVR integration
docker run -p 3000:3000 \
  -e HVR_API_BASE_URL=http://hvr-server:4340 \
  -e HVR_API_USERNAME=admin \
  -e HVR_API_PASSWORD=secure-password \
  -e HVR_INTEGRATED_MODE=true \
  hvr6-client-python
```

### Using Docker Compose

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hvr-client:
    build: .
    environment:
      - HVR_API_BASE_URL=http://hvr-server:4340
      - HVR_API_USERNAME=admin
      - HVR_API_PASSWORD=${HVR_PASSWORD}
      - HVR_INTEGRATED_MODE=true
    networks:
      - hvr-network

networks:
  hvr-network:
    external: true
```

Then run:

```bash
export HVR_PASSWORD=your-password
docker-compose up -d
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Use HTTPS** - Configure TLS for HVR API
3. **Rotate passwords** - Change credentials regularly
4. **Restrict access** - Use firewall rules and network policies
5. **Monitor logs** - Check for unauthorized access attempts

## Additional Resources

- [HVR 6.0 Documentation](https://docs.fivetran.com/hvr6/)
- [HVR REST API Reference](https://docs.fivetran.com/hvr6/api)
- [Python Client README](./README.md)

## Support

For issues specific to:
- **HVR 6.0**: Contact Fivetran support
- **Python Client**: Open an issue on GitHub
