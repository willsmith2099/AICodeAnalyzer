# Docker Deployment Files

This directory contains all Docker-related configuration files for the AI Code Analyzer.

## Files

- **Dockerfile** - Container image definition
- **docker-compose.yml** - Multi-service orchestration configuration
- **deploy.sh** - Deployment automation script

## Quick Start

### Start All Services

```bash
# From project root
cd docker
docker-compose up -d

# Or use the deployment script
./deploy.sh start
```

### Services

The docker-compose configuration includes:

1. **Ollama** (Port 11434)
   - Local LLM runtime
   - Model: qwen2.5:0.5b

2. **API Server** (Port 8000)
   - REST API for code analysis
   - Endpoint: http://localhost:8000

3. **Web UI** (Port 5001)
   - Modern web interface
   - URL: http://localhost:5001

4. **Neo4j** (Ports 7474, 7687)
   - Graph database
   - Browser: http://localhost:7474
   - Credentials: neo4j/password

### Pull Ollama Model

```bash
docker-compose exec ollama ollama pull qwen2.5:0.5b
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f neo4j
```

### Stop Services

```bash
docker-compose down

# Or use deployment script
./deploy.sh stop
```

### Clean Up

```bash
# Stop and remove volumes
docker-compose down -v

# Or use deployment script
./deploy.sh clean
```

## Environment Variables

You can customize the configuration using environment variables:

```bash
# Neo4j
export NEO4J_AUTH=neo4j/your_password

# Ollama
export OLLAMA_API_URL=http://ollama:11434
```

## Volumes

Persistent data is stored in Docker volumes:

- `ollama_data` - Ollama models and data
- `neo4j_data` - Neo4j graph database
- `neo4j_logs` - Neo4j logs

## Health Checks

All services include health checks:

- Ollama: `/api/tags`
- API: `/api/v1/health`
- Web: `/health`
- Neo4j: Cypher query test

## Troubleshooting

### Service won't start

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs [service-name]

# Restart service
docker-compose restart [service-name]
```

### Port conflicts

If ports are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change external port
```

### Reset everything

```bash
./deploy.sh clean
./deploy.sh start
```

## Documentation

- Main README: [../README.md](../README.md)
- Deployment Guide: [../DOCKER_DEPLOY.md](../DOCKER_DEPLOY.md)
- Neo4j Guide: [../NEO4J_GUIDE.md](../NEO4J_GUIDE.md)
