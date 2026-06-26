# Extract Platform

🇫🇷 Une plateforme d’extraction intelligente de documents financiers avec Docling  
🇬🇧 A smart platform for extracting financial documents with Docling

## Overview

Extract Platform is a distributed system for intelligent document extraction and processing. It combines modern document understanding (Docling) with a microservices architecture to extract, retrieve, and store structured data from financial documents.

## Architecture

### Services

- **Extract Service** (`extract/`) - Intelligent document extraction using Docling and custom pipelines
- **Main Service** (`main_service/`) - Central orchestration and document management
- **Store Service** (`store_data/`) - Document storage and database management
- **Retrieve Service** (`retrieve/`) - Information retrieval and document querying
- **Frontend** (`frontend/`) - React-based web interface for document upload and management

## Requirements

- Docker & Docker Compose
- Python 3.9+
- Node.js 16+ (for frontend)
- GPU (optional, for faster extraction)

## Quick Start

### Using Docker Compose

```bash
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Main API: http://localhost:8000
- Extract: http://localhost:8001
- Store: http://localhost:8002
- Retrieve: http://localhost:8003

### Local Development

#### Backend

```bash
# Extract service
cd extract
pip install -r requirements.txt
python app/extract_main.py

# Main service
cd main_service
pip install -r requirements.txt
uvicorn app.main:app --reload

# Store service
cd store_data
alembic upgrade head
python -m app.main
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Environment variables are configured via `.env`. See `.env.example` for available options.

### GPU Setup

For GPU acceleration, see `GPU_SETUP.md` for detailed instructions.

## Documentation

- `FRONTEND_SETUP.md` - Frontend development and build guide
- `GPU_SETUP.md` - GPU configuration for document extraction
- API documentation available at `/docs` endpoints on each service

## Development

All services expose FastAPI `/docs` endpoints for interactive API exploration.

## License

MIT 
