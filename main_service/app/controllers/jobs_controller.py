from fastapi import APIRouter, HTTPException, Query
from app.schemas.document_schemas import JobUpdate
from app.services.orchestration_service import (
    get_job, list_jobs, update_job_proxy, delete_job
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", status_code=200)
async def get_job_route(job_id: int):
    """Get single job."""
    try:
        job = await get_job(job_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", status_code=200)
async def list_jobs_route(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=10000)):
    """List all jobs."""
    try:
        jobs = await list_jobs(skip, limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{job_id}", status_code=200)
async def update_job_route(job_id: int, data: JobUpdate):
    """Update job."""
    try:
        updated = await update_job_proxy(job_id, data.model_dump(exclude_unset=True))
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}", status_code=204)
async def delete_job_route(job_id: int):
    """Delete job."""
    try:
        await delete_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
