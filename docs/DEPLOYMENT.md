# Deployment Guide

## Overview

This guide covers deploying Railway Work Access Port to production environments.

## Development Environment

### Prerequisites
- Python 3.10+
- pip or poetry
- SQLite (default) or PostgreSQL

### Setup

```bash
# Clone repository
git clone https://github.com/Landmind23/Railway-work-access-port.git
cd Railway-work-access-port

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python src/db/init.py

# Run development server
python src/main.py
```

### Running Tests

```bash
python -m unittest discover -s tests -v
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser
USER appuser

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:create_app()"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DATABASE_URL: postgresql://user:password@db:5432/railway
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped
    
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: railway
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t railway-work-access-port .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: railway-api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: railway-api
  template:
    metadata:
      labels:
        app: railway-api
    spec:
      containers:
      - name: api
        image: railway-work-access-port:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: railway-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: railway-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: railway-api-service
  namespace: production
spec:
  selector:
    app: railway-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace production

# Create secrets
kubectl create secret generic railway-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=secret-key=... \
  -n production

# Deploy application
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -n production
kubectl get services -n production
```

## Nginx Configuration

### Reverse Proxy

```nginx
upstream railway_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name api.railway-access-port.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.railway-access-port.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/api.railway-access-port.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.railway-access-port.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Logging
    access_log /var/log/nginx/railway_access.log combined;
    error_log /var/log/nginx/railway_error.log;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;
    
    # Proxy settings
    location /api/ {
        proxy_pass http://railway_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Production Configuration

### Environment Variables

```env
# Application
FLASK_ENV=production
FLASK_APP=src/main.py

# Database
DATABASE_URL=postgresql://user:password@db.example.com/railway
SQLALCHEMY_TRACK_MODIFICATIONS=false

# Security
SECRET_KEY=very-secure-random-key-min-32-chars
JWT_SECRET_KEY=jwt-secret-key

# API
API_HOST=0.0.0.0
API_PORT=5000
API_RATE_LIMIT=1000

# CORS
CORS_ORIGINS=https://portal.railway-access-port.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Database Backup

```bash
# Backup PostgreSQL
pg_dump -h db.example.com -U user railway > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h db.example.com -U user railway < backup_20260519.sql

# Automated backups (cron)
0 2 * * * pg_dump -h db.example.com -U user railway | gzip > /backups/railway_$(date +\%Y\%m\%d).sql.gz
```

## Monitoring & Logging

### Application Monitoring

```python
# src/monitoring.py
import logging
from pythonjsonlogger import jsonlogger

# JSON logging for structured logs
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Health Checks

```bash
# Kubernetes liveness probe
curl http://localhost:5000/api/v1/health

# Response
{
  "status": "healthy",
  "timestamp": "2026-05-19T10:30:00",
  "version": "0.1.0"
}
```

### Performance Monitoring

- Monitor response times
- Track error rates
- Monitor database query performance
- Track API rate limit usage

## Scaling

### Horizontal Scaling
- Deploy multiple API instances
- Use load balancer to distribute traffic
- Configure session management if needed

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching layer

## Rollback Plan

```bash
# If deployment fails
# 1. Check logs
docker-compose logs api

# 2. Rollback to previous version
docker-compose down
docker pull railway-work-access-port:previous-version
docker-compose up -d

# 3. Verify health
curl http://localhost:5000/api/v1/health
```

## Security Checklist

- [ ] HTTPS/SSL enabled
- [ ] SECRET_KEY changed from default
- [ ] Database credentials secure
- [ ] API tokens hashed
- [ ] Rate limiting configured
- [ ] CORS configured properly
- [ ] Logs secured
- [ ] Backups encrypted
- [ ] Firewall rules configured
- [ ] Regular security updates applied

---

**Last Updated**: May 2026
