# Extract Platform Architecture

## Overview

Extract Platform is a microservices-based document extraction system built with FastAPI and Docker. It orchestrates intelligent document processing through specialized services.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                    Port 80 / 3000 (dev)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
            ┌──────────────▼──────────────┐
            │    Main Service (Port 8000) │
            │   Orchestration & Routing   │
            └──┬──────────────┬──────────┬┘
               │              │          │
               ▼              ▼          ▼
         ┌─────────────┐ ┌─────────┐ ┌──────────────┐
         │   Extract   │ │ Retrieve│ │ Store Service│
         │Port 8001/   │ │Port 8002│ │  Port 8003   │
         │3001         │ │3002     │ │              │
         └─────────────┘ └─────────┘ │  ┌─────────┐│
                                     │  │Postgres ││
                                     │  │Database ││
                                     │  └─────────┘│
                                     └──────────────┘
```

## Service Layer

### 1. Frontend Service
- **Technology**: React + Vite
- **Port**: 80 (prod), 3000 (dev)
- **Responsibility**: Web UI for document upload and management
- **Communication**: HTTP REST to Main Service

### 2. Main Service (Orchestrator)
- **Technology**: FastAPI + Python
- **Port**: 8000
- **Responsibility**: 
  - Document lifecycle management
  - Service orchestration
  - Request routing
  - Job tracking

### 3. Extract Service
- **Technology**: FastAPI + Docling + VLM
- **Port**: 8001 (internal), 3001 (docker external)
- **Responsibility**:
  - Document extraction using Docling
  - VLM-based OCR via Nanonets
  - Multiple extraction profiles (fast, balanced, comprehensive)
  - GPU acceleration support

### 4. Retrieve Service
- **Technology**: FastAPI + Python
- **Port**: 8002 (internal), 3002 (docker external)
- **Responsibility**:
  - File retrieval and serving
  - Document metadata queries
  - Search and filtering

### 5. Store Service
- **Technology**: FastAPI + SQLAlchemy + PostgreSQL
- **Port**: 8003 (internal), 3003 (docker external)
- **Responsibility**:
  - Persistent document storage
  - Parse results management
  - Job history tracking
  - Database migrations (Alembic)

### 6. Database
- **Technology**: PostgreSQL 16
- **Port**: 5432 (internal), 3013 (docker external)
- **Responsibility**: 
  - Document metadata
  - Parse results
  - Job tracking
  - User data

## Communication Flow

### Document Upload & Processing Workflow

```
1. User uploads document via Frontend
   ↓
2. Main Service receives upload request
   ├─ Stores file (async to Retrieve)
   └─ Creates document record in Store
   ↓
3. Main Service triggers extraction (background task)
   ↓
4. Extract Service processes document
   ├─ Docling extracts content
   ├─ VLM refines extraction if needed
   └─ Returns content (markdown + JSON)
   ↓
5. Main Service stores results
   └─ Updates Store Service with parsed content
   ↓
6. Client polls Main Service for status
   ├─ Status: PENDING → PROCESSING → DONE/FAILED
   └─ Results available when DONE
```

### Key Endpoints

**Main Service**:
- `POST /documents` - Upload & extract (async)
- `GET /documents/{doc_id}` - Get document status
- `GET /documents/{doc_id}/parses` - Get extraction results
- `GET /jobs/{job_id}` - Track job progress

## Network Architecture

Services communicate via isolated Docker networks:

- **frontend-network**: Frontend ↔ Main Service
- **extract-network**: Main Service ↔ Extract Service
- **retrieve-network**: Main Service ↔ Retrieve Service
- **store-network**: Main Service ↔ Store Service
- **db-network**: Store Service ↔ PostgreSQL

This isolation ensures security and prevents cross-service interference.

## Data Flow

### Document Lifecycle

```
Document Upload (file bytes)
    ↓
File Storage (Retrieve Service)
    ↓
Document Record (Store Service)
    ↓
Extract Content (Extract Service)
    ↓
Parse Results (Store Service)
    ↓
Client Retrieval
```

### Supported Formats

- **Input**: PDF, DOCX, Images (PNG, JPG)
- **Output**: Markdown (default), JSON, Raw text

## Extraction Engines

### Classic Engine
- Uses Docling's OCR capabilities
- Multiple profiles: fast, balanced, comprehensive
- No external dependencies beyond Docling

### VLM Engine (Vision Language Model)
- Uses Nanonets OCR2 3B model
- Better handling of complex layouts
- Requires GPU for optimal performance
- More accurate for financial documents

## Storage Strategy

- **HuggingFace Cache** (`hf_cache` volume): Model weights (~3GB)
- **Retrieve Data** (`retrieve_data` volume): Uploaded files
- **PostgreSQL Data** (`postgres_data` volume): Metadata & results

This ensures:
- Fast model loading on restart
- Persistent document storage
- Reliable metadata persistence

## Scalability Considerations

### Current Limitations
- Single Extract worker (EXTRACT_WORKERS=1)
- Sequential processing

### Future Improvements
- Multiple Extract workers
- Job queue (Redis/RabbitMQ)
- Load balancing
- Horizontal scaling of services
