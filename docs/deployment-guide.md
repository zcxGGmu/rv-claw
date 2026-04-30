# RV-Claw Deployment Guide

## Overview

This guide covers the deployment of RV-Claw, a RISC-V contribution automation platform with dual-mode support (Chat and Pipeline).

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4 CPU cores, 8GB RAM minimum
- 50GB available disk space

## Quick Start

```bash
# Clone repository
git clone <repo-url>
cd rv-claw

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings

# Start all services
docker compose up -d

# Verify services
docker compose ps
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 80 | Vue.js SPA |
| backend | 8000 | FastAPI application |
| mongodb | 27017 | Document database |
| postgres | 5432 | LangGraph checkpointer |
| redis | 6379 | Cache and message broker |
| qemu-sandbox | - | Testing environment |

## Environment Variables

### Required

- `SECRET_KEY`: Random string for session encryption
- `BOOTSTRAP_ADMIN_USERNAME`: Default admin username
- `BOOTSTRAP_ADMIN_PASSWORD`: Default admin password
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

### Optional

- `MONGODB_URI`: MongoDB connection string
- `POSTGRES_URI`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Production Deployment

### 1. SSL/TLS Setup

```bash
# Using Let's Encrypt
certbot certonly --standalone -d your-domain.com

# Update docker-compose.yml to mount certificates
```

### 2. Database Backup

```bash
# MongoDB backup
docker compose exec mongodb mongodump --out /data/backup/$(date +%Y%m%d)

# PostgreSQL backup
docker compose exec postgres pg_dump -U rv rv_checkpoints > backup.sql
```

### 3. Monitoring

Services expose metrics endpoints:
- Backend: `/health` and `/ready`
- Prometheus metrics: `/metrics`

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose logs -f backend

# Verify environment
docker compose config
```

### Database Connection Issues

```bash
# Test MongoDB
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Test PostgreSQL
docker compose exec postgres pg_isready -U rv
```

## Updates

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d
```

## Security Checklist

- [ ] Change default admin password
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up log aggregation
- [ ] Enable automated backups
