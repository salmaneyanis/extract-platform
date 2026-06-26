# Database Documentation

PostgreSQL database schema and management for Extract Platform.

## Database Setup

### Connection

**Host**: `store_db` (docker) or `localhost:3013` (host)  
**Port**: 5432  
**Default User**: `postgres`  
**Default Password**: See `.env`  
**Default Database**: `extract_platform`

### Environment Configuration

In `.env`:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=extract_platform
```

### Connection String

From application:
```
postgresql+asyncpg://postgres:password@store_db:5432/extract_platform
```

From host:
```
postgresql://postgres:password@localhost:3013/extract_platform
```

## Schema

### Documents Table

Stores metadata about uploaded documents.

```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  file_name VARCHAR(255) NOT NULL,
  file_size BIGINT NOT NULL,
  file_path VARCHAR(512) NOT NULL UNIQUE,
  category VARCHAR(100),
  status VARCHAR(50) DEFAULT 'pending',
  stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_stored_at ON documents(stored_at DESC);
```

**Fields**:
- `id`: Unique identifier
- `file_name`: Original filename
- `file_size`: File size in bytes
- `file_path`: Path to stored file
- `category`: Document category (e.g., "invoice", "contract")
- `status`: Current status (pending, processing, done, failed)
- `stored_at`: When file was stored
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp

**Status Values**:
- `pending`: Awaiting processing
- `processing`: Currently being extracted
- `done`: Extraction completed
- `failed`: Extraction failed
- `archived`: Archived document

### Parses Table

Stores extraction results for documents.

```sql
CREATE TABLE parses (
  id SERIAL PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  job_id INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
  content_markdown TEXT,
  content_json JSONB,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parses_doc_id ON parses(doc_id);
CREATE INDEX idx_parses_job_id ON parses(job_id);
CREATE INDEX idx_parses_created_at ON parses(created_at DESC);
```

**Fields**:
- `id`: Unique identifier
- `doc_id`: Reference to document
- `job_id`: Reference to extraction job
- `content_markdown`: Extracted content in Markdown format
- `content_json`: Structured extraction in JSON
- `metadata`: Extraction metadata (engine, profile, language, etc.)
- `created_at`: Extraction timestamp
- `updated_at`: Last modification timestamp

**Metadata Example**:
```json
{
  "extraction_engine": "vlm",
  "profile": "comprehensive",
  "num_pages": 10,
  "language": "en",
  "confidence": 0.92,
  "processing_time_ms": 5432,
  "device_used": "cuda"
}
```

### Jobs Table

Tracks extraction job progress.

```sql
CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',
  result JSONB,
  error_message TEXT,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_doc_id ON jobs(doc_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
```

**Fields**:
- `id`: Unique identifier
- `doc_id`: Reference to document
- `status`: Job status (pending, processing, done, failed)
- `result`: Job result (parse_id, content preview, etc.)
- `error_message`: Error details if failed
- `started_at`: When extraction started
- `finished_at`: When extraction completed
- `created_at`: Job creation time
- `updated_at`: Last modification time

**Status Transitions**:
```
created → pending → processing → done (or failed)
```

**Result Example** (when done):
```json
{
  "parse_id": 42,
  "doc_id": 10,
  "status": "done",
  "content_preview": "# Invoice #INV-2024-001\n...",
  "processing_time_ms": 5432
}
```

## Data Relationships

```
documents (1) ──→ (many) parses
documents (1) ──→ (many) jobs
jobs (1) ──→ (1) parses (optional)
```

### Cascade Behavior

- **Deleting document**: Automatically deletes associated parses and jobs
- **Deleting job**: Sets job_id to NULL in related parses

## Migrations

Extract Platform uses Alembic for database schema management.

### Migration Files

Located in: `store_data/alembic/versions/`

### Running Migrations

#### Automatic (Docker)
Migrations run automatically on container startup.

#### Manual

```bash
cd store_data

# Show current version
alembic current

# Show migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one step
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision>
```

### Creating Migrations

```bash
cd store_data

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column"

# Manual migration
alembic revision -m "Custom migration"
```

### Migration Best Practices

- Always test migrations in development first
- Include both `upgrade()` and `downgrade()` implementations
- Use descriptive migration names
- Keep migrations small and focused
- Don't modify existing migration files (create new ones)

## Queries

### Document Statistics

```sql
-- Count documents by status
SELECT status, COUNT(*) as count
FROM documents
GROUP BY status;

-- Total storage used
SELECT SUM(file_size) as total_bytes
FROM documents;

-- Average processing time
SELECT AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) as avg_seconds
FROM jobs
WHERE status = 'done';
```

### Recent Extractions

```sql
-- Last 10 successful extractions
SELECT d.id, d.file_name, j.finished_at, p.id as parse_id
FROM documents d
JOIN jobs j ON d.id = j.doc_id
JOIN parses p ON j.id = p.job_id
WHERE j.status = 'done'
ORDER BY j.finished_at DESC
LIMIT 10;
```

### Failed Jobs

```sql
-- Failed extractions with error messages
SELECT j.id, d.file_name, j.error_message, j.finished_at
FROM jobs j
JOIN documents d ON j.doc_id = d.id
WHERE j.status = 'failed'
ORDER BY j.finished_at DESC;
```

### Document Search

```sql
-- Find documents by filename pattern
SELECT * FROM documents
WHERE file_name ILIKE '%invoice%'
ORDER BY stored_at DESC;

-- Find large documents
SELECT * FROM documents
WHERE file_size > 5000000  -- 5 MB
ORDER BY file_size DESC;
```

## Backup & Recovery

### Backup

```bash
# Dump entire database
docker exec extract-platform_store_db_1 pg_dump \
  -U postgres \
  extract_platform > backup.sql

# Dump with compression
docker exec extract-platform_store_db_1 pg_dump \
  -U postgres \
  -Fc \
  extract_platform > backup.dump
```

### Restore

```bash
# From SQL dump
docker exec -i extract-platform_store_db_1 psql \
  -U postgres \
  extract_platform < backup.sql

# From compressed dump
docker exec -i extract-platform_store_db_1 pg_restore \
  -U postgres \
  -d extract_platform \
  backup.dump
```

### Volume Backups

Database data persists in `postgres_data` volume. Backup the volume:

```bash
# Create backup
docker run --rm -v postgres_data:/data \
  -v backup:/backup \
  busybox tar czf /backup/postgres_backup.tar.gz -C / data

# Restore
docker run --rm -v postgres_data:/data \
  -v backup:/backup \
  busybox tar xzf /backup/postgres_backup.tar.gz -C /
```

## Performance Tuning

### Connection Pooling

SQLAlchemy uses connection pooling by default:
- Pool size: 10 connections
- Max overflow: 20 additional connections
- Pool recycle: 3600 seconds

Adjust in application code if needed.

### Query Optimization

Key indexes already created:
- `documents(status)` - Filter by status
- `documents(stored_at)` - Sort by date
- `parses(doc_id)` - Find parses for document
- `jobs(status)` - Filter jobs by status

Add more indexes for frequently used queries:

```sql
-- Example: If searching by file_name frequently
CREATE INDEX idx_documents_file_name ON documents(file_name);
```

### Maintenance

```bash
# Connect to database
docker exec -it extract-platform_store_db_1 psql \
  -U postgres \
  -d extract_platform

# Analyze table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Vacuum and analyze (maintenance)
VACUUM ANALYZE;

# List active connections
SELECT pid, usename, application_name, state
FROM pg_stat_activity
WHERE datname = 'extract_platform';
```

## Monitoring

### Key Metrics

- **Connection count**: Current/max connections
- **Query latency**: Average response time
- **Cache hit ratio**: Effective use of indexes
- **Database size**: Disk space usage

### Health Checks

```bash
# From host
psql -h localhost -U postgres -d extract_platform -c "SELECT 1"

# From docker network
docker exec extract-platform_store_db_1 psql \
  -U postgres \
  -d extract_platform \
  -c "SELECT 1"
```

## Troubleshooting

### Cannot connect to database

1. Check PostgreSQL container is running:
   ```bash
   docker ps | grep store_db
   ```

2. Check network connectivity:
   ```bash
   docker network ls
   docker network inspect extract-platform_db-network
   ```

3. Verify credentials in `.env`

### Slow queries

1. Enable query logging:
   ```sql
   SET log_statement = 'all';
   SET log_min_duration_statement = 1000;  -- Log queries > 1s
   ```

2. Analyze query plans:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM documents WHERE status = 'done';
   ```

### Disk space issues

```sql
-- Find largest tables
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Cleanup old records
DELETE FROM parses WHERE created_at < NOW() - INTERVAL '90 days';
VACUUM ANALYZE;
```

## Development Tools

### Access Database from Host

```bash
# psql (PostgreSQL CLI)
psql -h localhost -p 3013 -U postgres -d extract_platform

# DBeaver (GUI)
Connection: localhost:3013
User: postgres
Database: extract_platform
```

### View Logs

```bash
# PostgreSQL logs
docker logs extract-platform_store_db_1

# Follow logs
docker logs -f extract-platform_store_db_1
```
