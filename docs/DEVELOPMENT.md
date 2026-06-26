# Development Guide

Contributing to Extract Platform: setup, workflow, and best practices.

## Development Environment Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Git
- PostgreSQL client tools (optional)

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd extract-platform

# Copy environment file
cp .env.example .env

# Start Docker services
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Backend Development

### Python Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies for a service
cd extract
pip install -r requirements.txt

# Development dependencies (optional)
pip install pytest pytest-cov black flake8 mypy
```

### Running Services Locally

#### Extract Service

```bash
cd extract

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app/extract_main.py

# Or with auto-reload
uvicorn app.extract_main:app --reload --port 8001
```

#### Main Service

```bash
cd main_service

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.service_main:app --reload --port 8000
```

#### Store Service

```bash
cd store_data

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run service
uvicorn app.store_main:app --reload --port 8003
```

#### Retrieve Service

```bash
cd retrieve

pip install -r requirements.txt
python app/retrieve_main.py
```

### Project Structure

```
service/
├── app/
│   ├── __init__.py
│   ├── service_main.py          # FastAPI app entry point
│   ├── config.py                # Configuration
│   ├── controllers/             # Endpoint handlers
│   │   └── *_controller.py
│   ├── schemas/                 # Pydantic models
│   │   └── *_schemas.py
│   ├── services/                # Business logic
│   │   └── *_service.py
│   ├── models/                  # ORM models (store_data)
│   │   └── *.py
│   └── middleware/              # Custom middleware
│       └── *.py
├── requirements.txt
├── dockerfile
└── pytest.ini                   # Test configuration
```

### Code Style

```bash
# Format code with Black
black .

# Check code style
flake8 .

# Type checking
mypy app/

# Run linter/formatter before commit
pre-commit install
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_controllers.py

# Run specific test function
pytest tests/test_controllers.py::test_upload_document

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Creating New Endpoints

1. **Create schema** (if needed):
   ```python
   # app/schemas/new_schemas.py
   from pydantic import BaseModel

   class NewRequest(BaseModel):
       field: str
   ```

2. **Create controller method**:
   ```python
   # app/controllers/new_controller.py
   from fastapi import APIRouter
   from app.schemas.new_schemas import NewRequest

   router = APIRouter(prefix="/new", tags=["new"])

   @router.post("")
   async def create_item(request: NewRequest):
       return {"status": "created"}
   ```

3. **Register in main app**:
   ```python
   # app/service_main.py
   from app.controllers.new_controller import router as new_router
   app.include_router(new_router)
   ```

4. **Add tests**:
   ```python
   # tests/test_new_controller.py
   def test_create_item():
       response = client.post("/new", json={"field": "value"})
       assert response.status_code == 200
   ```

## Frontend Development

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env for development
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

### Running Development Server

```bash
npm run dev

# Application at http://localhost:5173
```

### Project Structure

```
frontend/
├── src/
│   ├── components/              # Reusable components
│   │   └── *.jsx
│   ├── pages/                   # Page components
│   │   ├── DocumentUpload.jsx
│   │   ├── DocumentList.jsx
│   │   └── DocumentDetail.jsx
│   ├── services/
│   │   └── api.js               # API client
│   ├── App.jsx                  # Root component
│   ├── App.css
│   └── main.jsx                 # Entry point
├── public/                       # Static files
├── vite.config.js               # Vite configuration
├── package.json
└── .env.local
```

### API Integration

File: `src/services/api.js`

```javascript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

// Upload document
export const uploadDocument = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  for (const [key, value] of Object.entries(options)) {
    formData.append(key, value);
  }

  return api.post('/documents', formData);
};

// Get document
export const getDocument = (docId) => {
  return api.get(`/documents/${docId}`);
};
```

### Adding UI Components

```jsx
// src/components/DocumentCard.jsx
import React from 'react';

export default function DocumentCard({ document }) {
  return (
    <div className="document-card">
      <h3>{document.file_name}</h3>
      <p>Status: {document.status}</p>
    </div>
  );
}
```

### Build & Production

```bash
# Build for production
npm run build

# Preview build locally
npm run preview

# Build output in dist/
```

## Database Development

### Running Migrations

```bash
cd store_data

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View history
alembic history
```

### Writing Migrations

```python
# alembic/versions/001_add_column.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('documents', sa.Column('new_field', sa.String(255)))

def downgrade():
    op.drop_column('documents', 'new_field')
```

### Database Access

```bash
# Connect to database
docker exec -it extract-platform_store_db_1 psql -U postgres -d extract_platform

# Run SQL query
docker exec extract-platform_store_db_1 psql \
  -U postgres \
  -d extract_platform \
  -c "SELECT COUNT(*) FROM documents;"
```

## Git Workflow

### Branch Naming

```
feature/description          # New feature
fix/issue-description        # Bug fix
refactor/area               # Refactoring
docs/what                   # Documentation
```

### Commit Messages

```
type(scope): subject

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat(extract): support VLM extraction engine

Add support for Vision Language Model-based extraction
using Nanonets OCR2 3B model.

Closes #123
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Push: `git push origin feature/my-feature`
4. Open PR with description:
   - What changed
   - Why it changed
   - Testing done
5. Address review comments
6. Merge when approved

## Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_schemas.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_controllers.py
│   └── test_workflows.py
└── e2e/
    └── test_upload_flow.py
```

### Writing Tests

```python
# tests/unit/test_services.py
import pytest
from app.services.docling_service import extract_content

@pytest.fixture
def sample_pdf():
    return b"PDF binary content..."

def test_extract_content(sample_pdf):
    result = extract_content(sample_pdf)
    assert "content" in result
    assert result["status"] == "done"

def test_extract_content_invalid_file():
    with pytest.raises(ValueError):
        extract_content(b"invalid")
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.service_main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_document():
    return {
        "file_name": "test.pdf",
        "file_size": 1000,
        "category": "invoice"
    }
```

## Debugging

### FastAPI Debug Mode

```python
# app/config.py
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# app/service_main.py
app = FastAPI(debug=DEBUG)
```

Set in environment:
```bash
export DEBUG=true
python app/service_main.py
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Document uploaded", extra={"doc_id": 123})
logger.error("Extraction failed", exc_info=True)
```

Configure in FastAPI:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debugging Tools

- **FastAPI Swagger UI**: http://localhost:8000/docs
- **PostgreSQL CLI**: `psql`
- **Docker logs**: `docker logs -f service_name`
- **Python debugger**: `import pdb; pdb.set_trace()`

## Performance Profiling

### Python

```python
# Profile a function
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... code to profile ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.print_stats()
```

### Database

```sql
-- Check slow queries
SET log_min_duration_statement = 1000;  -- 1 second

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM documents WHERE status = 'done';
```

## Docker Development

### Building Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build extract

# Build without cache
docker-compose build --no-cache
```

### Developing Inside Container

```bash
# Shell into container
docker-compose exec extract sh

# Run command in container
docker-compose exec extract python -m pytest

# View logs
docker-compose logs -f --tail=100 extract
```

## Documentation

### Adding Documentation

1. Create markdown file in `docs/`
2. Link from README or other docs
3. Use clear headings and code examples
4. Keep it updated with code changes

### API Documentation

Automatically generated from docstrings:

```python
@router.post("/documents", status_code=202)
async def upload_document(file: UploadFile):
    """
    Upload and extract document.

    **Parameters:**
    - `file`: PDF, DOCX, or image file

    **Returns:**
    - `doc_id`: Document identifier
    - `status`: Processing status
    """
    ...
```

Available at `/docs` endpoint.

## Troubleshooting

### Service won't connect

1. Check Docker network:
   ```bash
   docker network ls
   docker network inspect extract-platform_extract-network
   ```

2. Verify service is running:
   ```bash
   docker-compose logs extract
   ```

3. Test connectivity:
   ```bash
   docker-compose exec main_service \
     curl http://extract:8001/health
   ```

### Database errors

```bash
# Check database logs
docker-compose logs store_db

# Connect and verify
docker-compose exec store_db \
  psql -U postgres -d extract_platform -c "SELECT 1;"
```

### Port conflicts

```bash
# Find process using port
lsof -i :8000

# Change port in docker-compose.yaml
ports:
  - "8001:8000"  # external:internal
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Getting Help

1. Check existing documentation
2. Search GitHub issues
3. Review logs: `docker-compose logs -f`
4. Ask in team chat/email

## CI/CD (Future)

Planned integrations:
- GitHub Actions for automated tests
- Docker image builds and pushes
- Automated deployments
- Security scanning
