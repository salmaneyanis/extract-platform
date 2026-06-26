# Services Documentation

Detailed guide for each microservice in Extract Platform.

## Main Service

**Location**: `main_service/`  
**Port**: 8000  
**Framework**: FastAPI  
**Purpose**: Central orchestration and document lifecycle management

### Architecture

```
FastAPI App
├── Controllers
│   ├── document_controller.py
│   ├── parses_controller.py
│   └── jobs_controller.py
├── Schemas (Pydantic models)
│   └── document_schemas.py
└── Services
    └── orchestration_service.py
```

### Key Components

#### Document Controller
Handles document-related requests:
- Upload & process document (POST /documents)
- Get document details (GET /documents/{id})
- List documents (GET /documents)
- Update document (PUT /documents/{id})
- Delete document (DELETE /documents/{id})
- Get document file (GET /documents/{id}/file)
- Get parse results (GET /documents/{id}/parses)

#### Parses Controller
Manages extraction results:
- Get parse details (GET /parses/{id})
- List parses (GET /parses)
- Delete parse (DELETE /parses/{id})

#### Jobs Controller
Tracks processing jobs:
- Get job status (GET /jobs/{id})
- List jobs (GET /jobs)
- Update job (PUT /jobs/{id})
- Delete job (DELETE /jobs/{id})

#### Orchestration Service
Core business logic:
- `process_document()` - Orchestrate full pipeline
- `upload_document()` - Save file to Retrieve service
- `extract_and_save()` - Call Extract service, store results
- `get_document()` / `list_documents()` - Fetch from Store service
- `get_parse()` / `list_parses()` - Retrieve extraction results

### Data Models

#### Document
```python
{
  "doc_id": int,
  "file_name": str,
  "file_size": int,
  "file_path": str,
  "category": str,
  "stored_at": datetime,
  "status": Status
}
```

#### Job
```python
{
  "job_id": int,
  "doc_id": int,
  "status": Status,  # pending, processing, done, failed
  "result": dict,
  "error_message": str | None,
  "started_at": datetime,
  "finished_at": datetime
}
```

### Processing Flow

1. **Upload Request** → POST /documents
   - Validate file
   - Upload to Retrieve service
   - Create document record in Store
   - Return 202 Accepted with doc_id

2. **Background Extraction**
   - Create job record
   - Call Extract service (async)
   - Extract content
   - Store parse results
   - Update job status

3. **Status Polling**
   - Client polls GET /documents/{doc_id}
   - Returns current status
   - When done, client gets parse results

### Environment Variables

None required. Service discovers other services via docker-compose network.

### Dependencies

- fastapi
- httpx (HTTP client)
- pydantic (validation)

---

## Extract Service

**Location**: `extract/`  
**Port**: 8001 (internal), 3001 (docker)  
**Framework**: FastAPI  
**Purpose**: Intelligent document extraction

### Architecture

```
FastAPI App
├── Controllers
│   └── extract_controller.py
├── Schemas
│   └── extract_schemas.py
├── Services
│   ├── docling_service.py
│   └── pipeline_service.py
└── Models (HF cache)
```

### Key Components

#### Extract Controller
Single endpoint: `POST /extract`
- Receives file + extraction parameters
- Delegates to extraction pipeline
- Returns extracted content + metadata

#### Docling Service
Wrapper around Docling library:
- Load and parse documents
- Extract content and structure
- Support multiple output formats
- Handle errors gracefully

#### Pipeline Service
Manages extraction workflow:
- Route to correct engine (classic vs VLM)
- Apply selected profile
- Manage device allocation (CPU/GPU)
- Format output

### Extraction Engines

#### Classic Engine
- **Engine**: Docling built-in OCR
- **Profiles**:
  - `fast`: Quick extraction, 10-20% loss
  - `balanced`: Good speed/quality tradeoff
  - `comprehensive`: Best quality, slow
- **Device**: CPU or GPU
- **Use Case**: Speed-critical applications

#### VLM Engine
- **Model**: Nanonets OCR2 3B (Vision Language Model)
- **Input**: Document images
- **Output**: Structured extraction
- **Device**: GPU recommended
- **Use Case**: Complex layouts, financial documents

### Extraction Process

```
Input Document
    ↓
Load via Docling
    ↓
Convert to images
    ↓
Apply Engine
├─ Classic: Direct OCR
└─ VLM: Send to Nanonets via Docling
    ↓
Extract Content
    ├─ Markdown
    ├─ JSON (structured)
    └─ Metadata
    ↓
Return Results
```

### Response Format

```python
{
  "job_id": int,
  "doc_id": int,
  "parse_id": int,
  "status": Status,
  "content_markdown": str,
  "content_json": dict,
  "metadata": {
    "num_pages": int,
    "language": str,
    "confidence": float,
    "extraction_engine": str,
    "profile": str
  },
  "processing_time_ms": float,
  "device_used": str  # "cpu" or "cuda"
}
```

### Environment Variables

```bash
EXTRACT_DEFAULT_ENGINE=vlm          # classic or vlm
VLM_MODEL_ID=nanonets/Nanonets-OCR2-3B
VLM_MAX_NEW_TOKENS=4096
EXTRACT_WORKERS=1                   # Number of workers
EXTRACT_DEFAULT_DEVICE=auto         # auto, cpu, gpu
HF_HOME=/models/hf                  # HuggingFace cache location
```

### Dependencies

- docling (document extraction)
- torch (ML framework)
- transformers (VLM models)
- fastapi
- pydantic

### GPU Optimization

For GPU usage:
1. Install NVIDIA Container Toolkit on host
2. Docker compose automatically detects GPU
3. Set EXTRACT_DEFAULT_DEVICE=auto
4. Models cached in `hf_cache` volume (~3GB)

---

## Store Service

**Location**: `store_data/`  
**Port**: 8003 (internal), 3003 (docker)  
**Framework**: FastAPI + SQLAlchemy  
**Database**: PostgreSQL 16  
**Purpose**: Persistent data storage and management

### Architecture

```
FastAPI App
├── Controllers
│   ├── document_controller.py
│   ├── parses_controller.py
│   └── jobs_controller.py
├── Schemas
│   └── document_schemas.py
├── Models (ORM)
│   └── (in database)
├── Services
│   ├── persistence_service.py
│   ├── job_service.py
│   └── parse_service.py
├── Alembic Migrations
│   └── versions/
└── Database
    └── PostgreSQL
```

### Database Models

#### Document Table
```sql
documents (
  id: PK,
  file_name: str,
  file_size: int,
  file_path: str,
  category: str,
  status: str,
  stored_at: datetime
)
```

#### Parse Table
```sql
parses (
  id: PK,
  doc_id: FK,
  job_id: FK,
  content_markdown: text,
  content_json: jsonb,
  metadata: jsonb,
  created_at: datetime
)
```

#### Job Table
```sql
jobs (
  id: PK,
  doc_id: FK,
  status: str,
  result: jsonb,
  error_message: str,
  started_at: datetime,
  finished_at: datetime
)
```

### Key Services

#### Persistence Service
- CRUD operations for all entities
- Transaction management
- Data integrity

#### Job Service
- Job lifecycle management
- Status transitions
- Result storage

#### Parse Service
- Parse result management
- Content storage
- Metadata handling

### Database Migrations

Using Alembic for schema management:

```bash
# Create migration
alembic revision --autogenerate -m "Add column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
```

### Dependencies

- sqlalchemy (ORM)
- psycopg2-asyncpg (async PostgreSQL driver)
- alembic (migrations)
- fastapi
- pydantic

---

## Retrieve Service

**Location**: `retrieve/`  
**Port**: 8002 (internal), 3002 (docker)  
**Framework**: FastAPI  
**Storage**: File system + Metadata  
**Purpose**: File storage and retrieval

### Architecture

```
FastAPI App
├── Controllers
│   └── files_controller.py
├── Schemas
│   └── file_schemas.py
└── Services
    └── file_services.py
```

### Storage Layout

```
retrieve_data/
├── documents/
│   ├── {date}/
│   │   ├── file1.pdf
│   │   ├── file2.docx
│   │   └── ...
│   └── ...
└── temp/
    └── (temporary files)
```

### Key Endpoints

- `POST /files/upload` - Upload file
- `GET /files/{file_id}` - Download file
- `GET /files/{file_id}/metadata` - Get metadata
- `DELETE /files/{file_id}` - Delete file
- `GET /files` - List files

### File Management

- Automatic filename sanitization
- Duplicate detection
- Metadata tracking (size, type, upload time)
- Disk usage monitoring

### Dependencies

- fastapi
- python-multipart
- pydantic

---

## Frontend Service

**Location**: `frontend/`  
**Port**: 80 (prod), 3000 (dev)  
**Framework**: React + Vite  
**Purpose**: Web UI for document management

### Structure

```
src/
├── components/
│   └── (reusable UI components)
├── pages/
│   ├── DocumentUpload.jsx
│   ├── DocumentList.jsx
│   └── DocumentDetail.jsx
├── services/
│   └── api.js (HTTP client)
├── App.jsx
├── App.css
└── main.jsx
```

### Pages

#### Document Upload
- File selection (drag & drop)
- Engine/profile selection
- Upload progress
- Status polling

#### Document List
- All uploaded documents
- Filters by status
- Quick actions (view, delete)
- Pagination

#### Document Detail
- Full document information
- Extraction results (markdown + JSON)
- Job history
- Download options

### API Integration

File: `src/services/api.js`

Base URL configured via `VITE_API_URL` environment variable.

### Build & Development

```bash
# Development
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

### Dependencies

- react
- react-dom
- axios (HTTP client)
- vite (build tool)

---

## Service Communication

### Internal URLs (Docker Network)

```
Main Service → Extract: http://extract:8001
Main Service → Retrieve: http://retrieve:8002
Main Service → Store: http://store_data:8003
Store Service → PostgreSQL: postgresql://store_db:5432
Frontend → Main Service: http://main_service:8000
```

### External URLs (from Host)

```
http://localhost:8000     # Main Service
http://localhost:3001     # Extract Service
http://localhost:3002     # Retrieve Service
http://localhost:3003     # Store Service
http://localhost:3013     # PostgreSQL
http://localhost:80 or 3000 # Frontend
```

---

## Health Checks

Each service implements `GET /health`:

```json
{
  "status": "ok",
  "service": "Service Name"
}
```

Use for readiness/liveness probes in Kubernetes.

---

## Error Handling

All services follow standard HTTP error codes and response format:

```json
{
  "detail": "Human-readable error message"
}
```

Common errors:
- 400: Invalid input
- 404: Resource not found
- 422: Validation error
- 500: Internal server error

---

## Logging

Services log to console (stdout). In production, consider:
- ELK stack (Elasticsearch + Logstash + Kibana)
- Datadog/New Relic for APM
- CloudWatch for AWS deployments

---

## Performance Considerations

### Extract Service
- Single worker by default
- Scale horizontally with job queue
- GPU acceleration for VLM engine

### Store Service
- Connection pooling enabled
- Async database operations
- Index important columns

### Frontend
- Code splitting via Vite
- Asset caching headers
- Lazy loading for document list

---

## Monitoring

Key metrics to track:
- Extract service: Processing time, success rate, GPU usage
- Store service: Query latency, database connections
- Main service: Request latency, error rate
- Frontend: Page load time, user interactions
