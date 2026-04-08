# Docker Deployment Guide

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- Groq API key

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Build Vector Database (First Time Only)

```bash
# On Windows
docker run --rm -v "%cd%\data:/app/data" -v "%cd%\app:/app/app" python:3.11-slim sh -c "pip install sentence-transformers && python /app/app/db/ingest.py"

# On Linux/Mac
docker run --rm -v "$(pwd)/data:/app/data" -v "$(pwd)/app:/app/app" python:3.11-slim sh -c "pip install sentence-transformers && python /app/app/db/ingest.py"
```

Or use the batch file:
```bash
rebuild_db.bat
```

### 3. Start All Services

```bash
docker-compose up -d
```

This starts:
- RabbitMQ (message broker)
- API server (port 8000)
- Worker (2 instances for redundancy)

### 4. Verify Services

Check status:
```bash
docker-compose ps
```

Check logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

### 5. Test the API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My wound is swollen",
    "pain_level": 5,
    "discomfort_level": 6,
    "dl_output": {"infection_detected": false}
  }'
```

### 6. Access RabbitMQ Management UI

Open browser: http://localhost:15672
- Username: `guest`
- Password: `guest`

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Restart a specific service
```bash
docker-compose restart worker
docker-compose restart api
```

### View logs
```bash
docker-compose logs -f worker
```

### Scale workers
```bash
docker-compose up -d --scale worker=5
```

### Rebuild after code changes
```bash
docker-compose build
docker-compose up -d
```

### Clean everything (including volumes)
```bash
docker-compose down -v
```

## Production Deployment

### 1. Build optimized image
```bash
docker build -t medical-chatbot:latest .
```

### 2. Use production docker-compose
Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: medical-chatbot:latest
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CLOUDAMQP_URL=${CLOUDAMQP_URL}  # Use CloudAMQP in prod
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    restart: always

  worker:
    image: medical-chatbot:latest
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CLOUDAMQP_URL=${CLOUDAMQP_URL}
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: always
```

### 3. Deploy
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Groq API key for LLM |
| `CLOUDAMQP_URL` | No | `amqp://guest:guest@rabbitmq:5672/` | RabbitMQ connection URL |

## Troubleshooting

### Worker not processing tasks
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

### RabbitMQ connection refused
```bash
# Check if RabbitMQ is healthy
docker-compose ps rabbitmq

# Check RabbitMQ logs
docker-compose logs rabbitmq
```

### API not responding
```bash
# Check API logs
docker-compose logs api

# Check health
curl http://localhost:8000/
```

### Rebuild vector database
```bash
# Stop all services
docker-compose down

# Delete old data
rm data/vector_store.*

# Rebuild database
docker-compose run --rm api python app/db/ingest.py

# Restart services
docker-compose up -d
```

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       v
┌─────────────────┐
│   API Server    │ (Port 8000)
│   (FastAPI)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   RabbitMQ      │ (Port 5672)
│   (Message Q)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Workers (2+)  │
│   (Consumer)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Groq LLM API   │
└─────────────────┘
```

## Volume Mounts

- `./data:/app/data` - Persistent storage for:
  - Vector database (vector_store.index, vector_store.json)
  - Results (results.json)

## Network

All services communicate via `chatbot_network` bridge network.

## Health Checks

- **API**: HTTP GET to `/` every 30s
- **RabbitMQ**: Built-in diagnostics every 10s
- **Worker**: No health check (stateless consumer)

## Security Notes

1. **Non-root user**: Container runs as user `chatbot` (UID 1000)
2. **No authentication**: Deploy behind API gateway
3. **API key**: Stored in environment variable
4. **Network isolation**: Services isolated in bridge network

## Resource Limits (Production)

Recommended limits per container:
- API: 512MB RAM, 0.5 CPU
- Worker: 512MB RAM, 0.5 CPU
- RabbitMQ: 1GB RAM, 1 CPU

## Monitoring

Add to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

## Backup

Backup vector database:
```bash
docker cp medical_chatbot_api:/app/data/vector_store.index ./backup/
docker cp medical_chatbot_api:/app/data/vector_store.json ./backup/
```

## License

See LICENSE file.
