from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.document_schemas import (
    JobCreate,
    JobUpdate,
    JobResponse,
)
from app.services.job_service import (
    create_job,
    get_job,
    list_jobs,
    update_job,
    delete_job,
)

from app.services.exceptions import (
    DatabaseError,
    JobNotFoundError,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", status_code=201, response_model=JobResponse)
async def create( data: JobCreate,db: AsyncSession = Depends(get_db)):
    return await create_job(db, data)

@router.get("/{job_id}", response_model=JobResponse)
async def get(job_id: int, db: AsyncSession = Depends(get_db) ):
    try:
        return await get_job(db,job_id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=404,detail=str(e))

@router.get("", response_model=list[JobResponse])
async def get_all(skip: int = Query(0,ge=0), limit: int = Query(100, ge=1, le=10000) ,db: AsyncSession = Depends(get_db)):
    return await list_jobs(db,skip,limit)


@router.patch("/{job_id}", response_model=JobResponse)
async def update(job_id: int, data: JobUpdate, db: AsyncSession = Depends(get_db)):
    return await update_job(db, job_id, data)

@router.delete("/{job_id}", status_code=204) 
async def delete(job_id: int, db: AsyncSession = Depends(get_db)):
    await delete_job(db, job_id)


 