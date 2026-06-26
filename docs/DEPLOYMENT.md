# Deployment Guide

Production deployment and infrastructure considerations for Extract Platform.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] SSL/TLS certificates prepared
- [ ] Monitoring and logging setup
- [ ] Backup strategy documented
- [ ] Security audit completed

## Docker Compose Deployment

### Quick Start

```bash
# Clone repository
git clone <repo-url>
cd extract-platform

# Configure environment
cp .env.example .env
# Edit .env with production values

# Start services
docker-compose up -d

# Check service health
docker-compose ps
curl http://localhost:8000/health
```

### Service Status

```bash
# View logs
docker-compose logs -f main_service

# Restart service
docker-compose restart extract

# Stop all
docker-compose down

# Stop and remove volumes (⚠️ DATA LOSS)
docker-compose down -v
```

## Production Environment Variables

Create `.env.production`:

```bash
# PostgreSQL
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=extract_platform

# Extract Service
EXTRACT_DEFAULT_ENGINE=vlm
EXTRACT_WORKERS=4              # Scale up for production
EXTRACT_DEFAULT_DEVICE=auto
HF_HOME=/models/hf

# API Configuration
CORS_ORIGINS=https://yourdomain.com
API_MAX_REQUESTS_PER_MINUTE=60  # Rate limiting (to implement)

# Optional: Monitoring
SENTRY_DSN=https://key@sentry.io/project
LOG_LEVEL=INFO
```

### Load via Docker

```bash
docker-compose --env-file .env.production up -d
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional)
- PersistentVolume provisioner

### Manifest Structure

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml
├── postgres/
│   ├── statefulset.yaml
│   ├── service.yaml
│   └── pvc.yaml
├── store-service/
├── extract-service/
├── retrieve-service/
├── main-service/
└── frontend/
```

### Example: Main Service Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: main-service
  namespace: extract-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: main-service
  template:
    metadata:
      labels:
        app: main-service
    spec:
      containers:
      - name: main-service
        image: extract-platform/main-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: EXTRACT_URL
          value: http://extract-service:8001
        - name: RETRIEVE_URL
          value: http://retrieve-service:8002
        - name: STORE_URL
          value: http://store-service:8003
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: main-service
  namespace: extract-platform
spec:
  selector:
    app: main-service
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace extract-platform

# Create secrets
kubectl create secret generic postgres-credentials \
  --from-literal=username=prod_user \
  --from-literal=password=<password> \
  -n extract-platform

# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -n extract-platform
kubectl logs -f deployment/main-service -n extract-platform

# Scale services
kubectl scale deployment/main-service --replicas=5 -n extract-platform
```

## Cloud Deployments

### AWS (ECS)

1. **Push images to ECR**:
   ```bash
   aws ecr create-repository --repository-name extract-platform
   docker build -t extract-platform/main-service .
   docker tag extract-platform/main-service:latest \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com/extract-platform:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/extract-platform:latest
   ```

2. **Create RDS PostgreSQL instance**:
   - Multi-AZ for high availability
   - Automated backups
   - Read replicas for scaling

3. **Create ECS Task Definition** with environment variables pointing to RDS

4. **Deploy with CloudFormation or Terraform**

### Google Cloud (GKE)

```bash
# Create cluster
gcloud container clusters create extract-platform \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --zone us-central1-a

# Push images
gcloud builds submit --tag gcr.io/PROJECT_ID/extract-platform

# Deploy
kubectl apply -f k8s/
```

### Azure (AKS)

```bash
# Create cluster
az aks create --resource-group extract-platform \
  --name extract-cluster \
  --node-count 3

# Get credentials
az aks get-credentials --resource-group extract-platform \
  --name extract-cluster

# Deploy
kubectl apply -f k8s/
```

## SSL/TLS Configuration

### Using Let's Encrypt with Docker

1. **Install Certbot**:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Get Certificate**:
   ```bash
   sudo certbot certonly --standalone \
     -d yourdomain.com \
     -d www.yourdomain.com
   ```

3. **Configure Nginx (reverse proxy)**:
   ```nginx
   server {
     listen 443 ssl http2;
     server_name yourdomain.com;

     ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
     ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

     location / {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
     }
   }
   ```

4. **Mount certificates in docker-compose**:
   ```yaml
   volumes:
     - /etc/letsencrypt:/etc/letsencrypt:ro
   ```

### Kubernetes with cert-manager

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager

# Create certificate
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: extract-platform-cert
spec:
  secretName: extract-platform-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - yourdomain.com
EOF
```

## Reverse Proxy Setup

### Nginx Configuration

```nginx
upstream extract_platform {
  server localhost:8000;
}

server {
  listen 80;
  server_name yourdomain.com;

  # Redirect HTTP to HTTPS
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name yourdomain.com;

  # SSL certificates
  ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

  # Security headers
  add_header Strict-Transport-Security "max-age=31536000" always;
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;

  # Compression
  gzip on;
  gzip_types text/plain application/json;

  # Main API
  location /api {
    proxy_pass http://extract_platform;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    client_max_body_size 100M;  # Max upload size
  }

  # Frontend
  location / {
    proxy_pass http://extract_platform;
    proxy_set_header Host $host;
  }

  # Health check
  location /health {
    access_log off;
    proxy_pass http://extract_platform;
  }
}
```

## Monitoring & Logging

### Prometheus Metrics

Add Prometheus endpoint to FastAPI services:

```python
from prometheus_client import Counter, Histogram

requests_total = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)
```

Scrape configuration:
```yaml
scrape_configs:
  - job_name: 'extract-platform'
    static_configs:
      - targets: ['localhost:8000', 'localhost:8001', 'localhost:8003']
```

### ELK Stack (Elasticsearch + Logstash + Kibana)

1. **Configure logging in Python**:
   ```python
   import logging
   import json

   class JsonFormatter(logging.Formatter):
       def format(self, record):
           return json.dumps({
               'timestamp': self.formatTime(record),
               'level': record.levelname,
               'message': record.getMessage(),
               'service': 'extract-service'
           })
   ```

2. **Configure Logstash** to consume logs
3. **View in Kibana dashboard**

### Key Metrics to Monitor

- **Extract Service**:
  - Processing time per document
  - Success/failure rates
  - GPU utilization
  - Queue depth

- **Store Service**:
  - Query latency
  - Database connections
  - Disk usage

- **Main Service**:
  - Request latency
  - Error rates
  - Concurrent users

- **Frontend**:
  - Page load time
  - API response time
  - User interactions

## Backup Strategy

### Database Backups

```bash
# Daily backups
0 2 * * * docker exec extract-platform_store_db_1 \
  pg_dump -U postgres extract_platform | \
  gzip > /backups/extract_db_$(date +\%Y\%m\%d).sql.gz
```

### Document Storage Backups

- Use S3/GCS for document storage
- Enable versioning
- Set lifecycle policies for old files

### Backup Retention

```
Daily:   Keep 7 days
Weekly:  Keep 4 weeks
Monthly: Keep 12 months
```

## Scaling Strategies

### Horizontal Scaling

1. **Extract Service**: Add more workers
   ```bash
   EXTRACT_WORKERS=8  # Increase workers
   ```

2. **Main Service**: Use load balancer
   ```yaml
   replicas: 5  # Kubernetes
   ```

3. **Store Service**: Read replicas for PostgreSQL
   ```sql
   -- Create read replica
   SELECT pg_create_physical_replication_slot('replica_slot');
   ```

### Vertical Scaling

- Increase CPU/memory limits
- Use GPU-enabled nodes for Extract service
- Optimize database indexes

### Caching

- Redis for session caching
- Frontend asset caching with CDN
- Database query caching

## Security Hardening

### Firewall Rules

```bash
# Allow only HTTPS
sudo ufw allow 443/tcp
sudo ufw deny 80/tcp  # Or redirect to HTTPS

# Restrict API access
sudo ufw allow from 10.0.0.0/8 to any port 8000
```

### API Security

- [ ] Implement authentication (JWT)
- [ ] Rate limiting per IP/user
- [ ] Input validation
- [ ] SQL injection prevention (SQLAlchemy)
- [ ] CORS properly configured
- [ ] HTTPS enforced

### Container Security

```bash
# Run as non-root
docker build --user 1000:1000

# Read-only filesystem
docker run --read-only
```

### Database Security

```bash
# Change default password
ALTER USER postgres WITH PASSWORD 'strong_password';

# Create restricted user
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

## Disaster Recovery

### Recovery Time Objective (RTO): 1 hour
### Recovery Point Objective (RPO): 1 day

### Procedures

1. **Database corruption**:
   ```bash
   # Restore from backup
   docker exec -i store_db psql -U postgres < backup.sql
   ```

2. **Service failure**:
   ```bash
   # Restart service
   docker-compose restart extract
   ```

3. **Complete data loss**:
   ```bash
   # Restore from S3/backup location
   aws s3 cp s3://backups/extract_db.sql.gz .
   gunzip extract_db.sql.gz
   docker exec -i store_db psql -U postgres < extract_db.sql
   ```

## Performance Tuning

### PostgreSQL

```sql
-- Increase shared_buffers (25% of RAM)
shared_buffers = 4GB

-- Increase work_mem for sorting
work_mem = 16MB

-- Optimize for sequential scans
random_page_cost = 1.1
```

### Application

- Enable query result caching
- Optimize database queries (add indexes)
- Use connection pooling
- Implement lazy loading in frontend

## Maintenance

### Regular Tasks

- [ ] Monitor disk space
- [ ] Review logs for errors
- [ ] Update dependencies (monthly)
- [ ] Test backups (monthly)
- [ ] Review security logs
- [ ] Update SSL certificates (60 days before expiry)

### Update Procedure

```bash
# 1. Test in staging
git checkout staging
docker-compose pull
docker-compose up -d

# 2. Run migrations
docker-compose exec store_data alembic upgrade head

# 3. Verify health
curl http://localhost:8000/health

# 4. Deploy to production
git checkout main
git pull
docker-compose up -d
```

## Support & Troubleshooting

### Common Issues

**Services won't start**:
```bash
docker-compose logs -f
docker-compose down
docker-compose up -d --build
```

**Database connection issues**:
```bash
docker-compose exec store_db psql -U postgres -c "SELECT 1"
```

**Out of disk space**:
```bash
docker system prune -a  # Remove unused images/containers
```

**High memory usage**:
```bash
docker stats  # Monitor resource usage
```

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md)
- [Services Documentation](SERVICES.md)
- [API Reference](API.md)
- [Database Guide](DATABASE.md)
- [Development Guide](../FRONTEND_SETUP.md)
- [GPU Setup](../GPU_SETUP.md)
