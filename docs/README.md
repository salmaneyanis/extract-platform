# Extract Platform Documentation

Complete documentation for the Extract Platform project.

## Quick Navigation

### Getting Started

1. **[README.md](../README.md)** - Project overview and quick start
2. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Local development setup and workflow

### Understanding the System

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - High-level system design and data flow
2. **[SERVICES.md](SERVICES.md)** - Detailed documentation of each microservice

### Integration & APIs

1. **[API.md](API.md)** - Complete REST API reference with examples
2. **[DATABASE.md](DATABASE.md)** - Database schema, queries, and management

### Deployment & Operations

1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide and infrastructure
2. **[GPU_SETUP.md](../GPU_SETUP.md)** - GPU configuration for acceleration
3. **[FRONTEND_SETUP.md](../FRONTEND_SETUP.md)** - Frontend development details

## Document Index

### Architecture & Design

| Document | Purpose | Audience |
|----------|---------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, service interactions, data flow | Architects, Team Leads |
| [SERVICES.md](SERVICES.md) | Service-by-service breakdown, components | Developers, DevOps |

### API & Integration

| Document | Purpose | Audience |
|----------|---------|----------|
| [API.md](API.md) | REST endpoints, request/response formats, examples | Developers, Frontend |
| [DATABASE.md](DATABASE.md) | Schema, queries, backups, optimization | Backend, DevOps |

### Development

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Local setup, coding standards, testing | Developers |
| [../FRONTEND_SETUP.md](../FRONTEND_SETUP.md) | React development, components, build | Frontend Developers |
| [../GPU_SETUP.md](../GPU_SETUP.md) | GPU configuration and optimization | DevOps, ML Engineers |

### Operations

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment, scaling, monitoring | DevOps, SRE |

## Common Tasks

### I want to...

#### Understand how the system works
→ Start with [ARCHITECTURE.md](ARCHITECTURE.md)

#### Set up local development
→ Follow [DEVELOPMENT.md](DEVELOPMENT.md)

#### Add a new API endpoint
→ Read [SERVICES.md](SERVICES.md) for structure, then [API.md](API.md) for conventions

#### Query the database
→ See [DATABASE.md](DATABASE.md) for schema and example queries

#### Deploy to production
→ Follow [DEPLOYMENT.md](DEPLOYMENT.md)

#### Optimize extraction performance
→ Check [GPU_SETUP.md](../GPU_SETUP.md) and [SERVICES.md](SERVICES.md#extract-service)

#### Build a frontend page
→ See [../FRONTEND_SETUP.md](../FRONTEND_SETUP.md) and [API.md](API.md)

#### Monitor the system
→ See [DEPLOYMENT.md](DEPLOYMENT.md#monitoring--logging)

#### Backup/restore data
→ Follow [DATABASE.md](DATABASE.md#backup--recovery)

## Architecture Overview

```
┌─────────────────────────┐
│   Frontend (React)      │
│   Port 80/3000          │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   Main Service (8000)   │
│   Orchestration         │
└────┬───────┬──────┬─────┘
     │       │      │
┌────▼──┐ ┌──▼──┐ ┌─▼──────────┐
│Extract│ │Retri│ │Store Service│
│8001   │ │8002 │ │8003 + DB    │
└───────┘ └─────┘ └─────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams and data flow.

## Key Services

### Extract Service
- Document extraction using Docling
- VLM-based OCR with Nanonets
- GPU acceleration support
- **Port**: 8001 (internal), 3001 (docker external)

### Main Service
- Orchestration and request routing
- Document lifecycle management
- Job tracking
- **Port**: 8000

### Store Service
- PostgreSQL database
- Document metadata storage
- Parse results persistence
- **Port**: 8003, Database 5432

### Retrieve Service
- File storage and retrieval
- Metadata management
- **Port**: 8002 (internal), 3002 (docker external)

### Frontend
- React web interface
- Document upload and management
- **Port**: 80 (production), 3000 (development)

## API Quick Reference

### Upload & Process Document
```bash
POST /documents
Content-Type: multipart/form-data

Parameters:
  file: Document file
  engine: "vlm" or "classic"
  profile: "fast", "balanced", or "comprehensive"
```

### Get Document Status
```bash
GET /documents/{doc_id}
```

### Get Extraction Results
```bash
GET /documents/{doc_id}/parses
```

See [API.md](API.md) for complete reference.

## Database Schema

**Main Tables:**
- `documents` - Document metadata
- `parses` - Extraction results
- `jobs` - Processing job tracking

See [DATABASE.md](DATABASE.md) for schema diagrams and queries.

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/description`
2. **Set up environment**: Follow [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Make changes and test**: Run `pytest`
4. **Commit with clear messages**: Follow [DEVELOPMENT.md](DEVELOPMENT.md#commit-messages)
5. **Create PR**: Link to issue, describe changes
6. **Address feedback**: Update code, re-test
7. **Merge when approved**: Delete feature branch

## Deployment Process

### Local/Docker
```bash
docker-compose up -d
```

### Production
See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Kubernetes deployment
- Cloud provider setup (AWS/GCP/Azure)
- SSL/TLS configuration
- Monitoring and logging

## Environment Configuration

Key variables (see `.env.example`):
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>
POSTGRES_DB=extract_platform
EXTRACT_DEFAULT_ENGINE=vlm
EXTRACT_WORKERS=1
EXTRACT_DEFAULT_DEVICE=auto
```

## Performance Tuning

- **Extract Service**: Increase EXTRACT_WORKERS, enable GPU
- **Store Service**: Database indexing, connection pooling
- **Frontend**: Asset caching, code splitting
- **Overall**: Use Nginx reverse proxy, CDN

See [DEPLOYMENT.md](DEPLOYMENT.md#performance-tuning).

## Monitoring

Key metrics:
- Extract processing time
- Database query latency
- API error rates
- User response times

See [DEPLOYMENT.md](DEPLOYMENT.md#monitoring--logging).

## Troubleshooting

### Services won't start
```bash
docker-compose logs -f
docker-compose down && docker-compose up -d --build
```

### Database connection issues
```bash
docker-compose exec store_db psql -U postgres -c "SELECT 1"
```

### High memory usage
```bash
docker stats
```

More troubleshooting in [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting) and [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting).

## Contributing

1. Read this documentation
2. Follow [DEVELOPMENT.md](DEVELOPMENT.md)
3. Write tests for new features
4. Document changes in relevant files
5. Follow commit message conventions

## FAQ

**Q: How do I enable GPU acceleration?**  
A: See [GPU_SETUP.md](../GPU_SETUP.md)

**Q: How do I add a new extraction profile?**  
A: See [SERVICES.md](SERVICES.md#extraction-engines)

**Q: How do I scale the system?**  
A: See [DEPLOYMENT.md](DEPLOYMENT.md#scaling-strategies)

**Q: Where are uploaded documents stored?**  
A: See [SERVICES.md](SERVICES.md#retrieve-service) for storage layout

**Q: How do I backup the database?**  
A: See [DATABASE.md](DATABASE.md#backup--recovery)

## Related Files

- Project README: [../README.md](../README.md)
- Frontend Setup: [../FRONTEND_SETUP.md](../FRONTEND_SETUP.md)
- GPU Configuration: [../GPU_SETUP.md](../GPU_SETUP.md)
- Environment Example: [../.env.example](../.env.example)
- Docker Compose: [../docker-compose.yaml](../docker-compose.yaml)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-06-26 | Complete documentation suite |

## License

This documentation is part of the Extract Platform project (MIT License).

## Document Metadata

- **Last Updated**: 2024-06-26
- **Status**: Complete
- **Maintained By**: Development Team
- **Review Cycle**: Quarterly

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Docling Guide](https://ds4sd.github.io/docling/)
