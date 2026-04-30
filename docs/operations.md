# RV-Claw Operations Manual

## Daily Operations

### Health Checks

```bash
# Check all services
docker compose ps

# Backend health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/ready
```

### Log Monitoring

```bash
# Real-time logs
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

## Maintenance

### Database Maintenance

**MongoDB:**
```bash
# Enter MongoDB shell
docker compose exec mongodb mongosh

# Check database stats
use rv_claw
db.stats()

# List collections
show collections
```

**PostgreSQL:**
```bash
# Enter PostgreSQL shell
docker compose exec postgres psql -U rv -d rv_checkpoints

# Check table sizes
\dt+
```

### Cleanup

```bash
# Remove old containers
docker compose down

# Clean up unused images
docker image prune -a

# Clean up volumes (WARNING: data loss)
docker volume prune
```

## Backup and Restore

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/$DATE

# MongoDB
docker compose exec mongodb mongodump --out /data/backup/$DATE

# PostgreSQL
docker compose exec postgres pg_dump -U rv rv_checkpoints > $BACKUP_DIR/postgres.sql

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
```

### Restore

```bash
# MongoDB restore
docker compose exec mongodb mongorestore /data/backup/YYYYMMDD

# PostgreSQL restore
docker compose exec -T postgres psql -U rv -d rv_checkpoints < backup.sql
```

## Alerting

### Webhook Integration

Configure webhook notifications for critical events:

```python
# config.py
ALERT_WEBHOOK_URL = "https://hooks.slack.com/services/..."
```

### Common Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| High CPU | > 80% for 5m | Scale backend containers |
| Disk Full | > 90% | Clean old artifacts |
| Pipeline Stuck | > 30m in stage | Manual intervention |

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.override.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Vertical Scaling

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Troubleshooting

### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart service
docker compose restart backend
```

### Slow Queries

```bash
# MongoDB slow queries
docker compose exec mongodb mongosh --eval "db.setProfilingLevel(2)"
```

### Pipeline Failures

1. Check case logs in MongoDB
2. Review SSE events in Redis
3. Check agent adapter logs
4. Verify resource limits

## Security

### Rotate Secrets

```bash
# Update .env
# Restart services
docker compose up -d
```

### Access Control

- Admin: Full access
- User: Create cases, view own cases
- Viewer: Read-only access

## Support

Contact: ops@example.com
Docs: https://docs.rv-claw.io
