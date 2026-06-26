# API Documentation

Complete reference for Extract Platform API endpoints.

## Base URLs

```
Main Service:     http://localhost:8000
Extract Service:  http://localhost:3001 (docker external)
Retrieve Service: http://localhost:3002 (docker external)
Store Service:    http://localhost:3003 (docker external)
```

## Interactive Documentation

Each service provides Swagger/OpenAPI docs:
- Main Service: http://localhost:8000/docs
- Extract Service: http://localhost:3001/docs
- Retrieve Service: http://localhost:3002/docs
- Store Service: http://localhost:3003/docs

## Main Service API

### Documents Endpoints

#### Upload & Extract Document
```http
POST /documents
Content-Type: multipart/form-data

Parameters:
  file: UploadFile (required) - Document file
  engine: str (optional, default="vlm") - "classic" or "vlm"
  profile: str (optional, default="balanced") - "fast", "balanced", "comprehensive"
  device: str (optional, default="auto") - "cpu", "gpu", "auto"
  output_format: str (optional, default="markdown") - "markdown", "json"

Response: 202 Accepted
{
  "doc_id": 1,
  "status": "processing",
  "message": "Document accepted for processing"
}
```

#### Get Document Status
```http
GET /documents/{doc_id}

Response: 200 OK
{
  "doc_id": 1,
  "file_name": "example.pdf",
  "file_size": 1024000,
  "file_path": "/uploads/example.pdf",
  "category": "financial",
  "stored_at": "2024-06-26T10:30:00Z",
  "status": "done"
}
```

#### List Documents
```http
GET /documents?skip=0&limit=10

Response: 200 OK
[
  {
    "doc_id": 1,
    "file_name": "document1.pdf",
    "status": "done",
    "stored_at": "2024-06-26T10:30:00Z"
  },
  ...
]
```

#### Update Document
```http
PUT /documents/{doc_id}
Content-Type: application/json

Body:
{
  "file_path": "/new/path",
  "status": "archived"
}

Response: 200 OK
{ ... updated document ... }
```

#### Delete Document
```http
DELETE /documents/{doc_id}

Response: 204 No Content
```

#### Get Document File
```http
GET /documents/{doc_id}/file

Response: 200 OK (file download)
```

#### Get Document Parses
```http
GET /documents/{doc_id}/parses

Response: 200 OK
[
  {
    "parse_id": 1,
    "doc_id": 1,
    "job_id": 1,
    "content_markdown": "# Document Title\n...",
    "content_json": { ... },
    "metadata": { ... }
  },
  ...
]
```

### Parses Endpoints

#### Get Parse Details
```http
GET /parses/{parse_id}

Response: 200 OK
{
  "parse_id": 1,
  "doc_id": 1,
  "job_id": 1,
  "content_markdown": "# Title\n...",
  "content_json": { ... },
  "metadata": { ... },
  "created_at": "2024-06-26T10:35:00Z"
}
```

#### List Parses
```http
GET /parses?skip=0&limit=10

Response: 200 OK
[
  {
    "parse_id": 1,
    "doc_id": 1,
    "content_markdown": "...",
    "created_at": "2024-06-26T10:35:00Z"
  },
  ...
]
```

#### Delete Parse
```http
DELETE /parses/{parse_id}

Response: 204 No Content
```

### Jobs Endpoints

#### Get Job Status
```http
GET /jobs/{job_id}

Response: 200 OK
{
  "job_id": 1,
  "doc_id": 1,
  "status": "done",
  "result": {
    "parse_id": 1,
    "content_markdown": "...",
    "processing_time_ms": 5432
  },
  "error_message": null,
  "started_at": "2024-06-26T10:32:00Z",
  "finished_at": "2024-06-26T10:35:00Z"
}
```

#### List Jobs
```http
GET /jobs?skip=0&limit=10&status=done

Response: 200 OK
[
  {
    "job_id": 1,
    "doc_id": 1,
    "status": "done",
    "started_at": "2024-06-26T10:32:00Z",
    "finished_at": "2024-06-26T10:35:00Z"
  },
  ...
]
```

#### Update Job
```http
PUT /jobs/{job_id}
Content-Type: application/json

Body:
{
  "status": "done",
  "result": { ... }
}

Response: 200 OK
{ ... updated job ... }
```

#### Delete Job
```http
DELETE /jobs/{job_id}

Response: 204 No Content
```

### Health Check

#### Service Health
```http
GET /health

Response: 200 OK
{
  "status": "ok",
  "service": "Main Service"
}
```

## Extract Service API

Internal service for document extraction.

### Extract Endpoints

#### Extract Document
```http
POST /extract
Content-Type: multipart/form-data

Parameters:
  file: UploadFile (required)
  engine: str (optional, default="vlm")
  profile: str (optional, default="balanced")
  device: str (optional, default="auto")
  output_format: str (optional, default="markdown")

Response: 200 OK
{
  "job_id": 1,
  "doc_id": 1,
  "parse_id": 1,
  "status": "done",
  "content_markdown": "# Title\n...",
  "content_json": { ... },
  "metadata": { ... },
  "processing_time_ms": 5432,
  "device_used": "cuda"
}
```

## Store Service API

Internal service for document persistence.

### Document Endpoints

#### Create Document
```http
POST /documents
Content-Type: application/json

Body:
{
  "file_name": "example.pdf",
  "file_size": 1024000,
  "file_path": "/uploads/example.pdf",
  "category": "financial"
}

Response: 201 Created
{ ... document record ... }
```

#### Get Document
```http
GET /documents/{doc_id}
```

#### List Documents
```http
GET /documents
```

#### Update Document
```http
PUT /documents/{doc_id}
```

### Parse Endpoints

#### Create Parse
```http
POST /parses
Content-Type: application/json

Body:
{
  "doc_id": 1,
  "job_id": 1,
  "content_markdown": "...",
  "content_json": { ... },
  "metadata": { ... }
}
```

### Job Endpoints

#### Create Job
```http
POST /jobs
Content-Type: application/json

Body:
{
  "doc_id": 1,
  "status": "processing"
}
```

#### Update Job
```http
PUT /jobs/{job_id}
Content-Type: application/json

Body:
{
  "status": "done",
  "result": { ... },
  "finished_at": "2024-06-26T10:35:00Z"
}
```

## Status Values

Jobs and documents support these status values:

| Status | Meaning |
|--------|---------|
| `pending` | Waiting to be processed |
| `processing` | Currently being processed |
| `done` | Successfully completed |
| `failed` | Processing failed |

## Error Responses

All endpoints return standard HTTP error codes:

```
400 Bad Request - Invalid input
401 Unauthorized - Authentication required
404 Not Found - Resource doesn't exist
422 Unprocessable Entity - Validation error
500 Internal Server Error - Server error
```

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Examples

### Complete Upload & Extract Workflow

```bash
# 1. Upload document
curl -X POST http://localhost:8000/documents \
  -F "file=@invoice.pdf" \
  -F "engine=vlm" \
  -F "profile=comprehensive"

# Response: 202 Accepted
# {
#   "doc_id": 42,
#   "status": "processing",
#   "message": "Document accepted for processing"
# }

# 2. Poll for completion
curl http://localhost:8000/documents/42

# Response while processing:
# {
#   "doc_id": 42,
#   "status": "processing",
#   ...
# }

# Response when done:
# {
#   "doc_id": 42,
#   "status": "done",
#   ...
# }

# 3. Get extraction results
curl http://localhost:8000/documents/42/parses

# Response:
# [
#   {
#     "parse_id": 1,
#     "content_markdown": "...",
#     "content_json": {...},
#     "created_at": "2024-06-26T10:35:00Z"
#   }
# ]
```

## Authentication

Currently, no authentication is required. All endpoints are public.

**Future**: JWT authentication will be implemented.

## Rate Limiting

No rate limiting is currently enforced. This should be added before production deployment.

## CORS

All endpoints allow Cross-Origin requests from any origin.
