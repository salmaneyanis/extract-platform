from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Job
from app.services.exceptions import JobNotFoundError, DatabaseError
from app.schemas.document_schemas import JobCreate, JobUpdate



async def create_job(db: AsyncSession, data: JobCreate) -> Job:
    """  """
    job = Job(
        doc_id=data.doc_id,
        job_type=data.job_type,
    )

    db.add(job)

    await db.commit()
    await db.refresh(job)
    return job



async def get_job(db: AsyncSession, job_id: int) -> Job | None:
    result = await db.execute(select(Job).where(Job.job_id == job_id))
    job = result.scalar_one_or_none()

    if job is None:
        raise JobNotFoundError(f"DocumentParse {job_id} introuvable")

    return job

async def list_jobs(db: AsyncSession,doc_id: int | None = None , skip: int = 0, limit: int = 100) -> list[Job]:
    
    if doc_id != None: 
        result = await db.execute(
            select(Job)
            .order_by(Job.created_at.desc())
            .where(Job.doc_id == doc_id)
            .limit(limit)
            .offset(skip)
        ) 
    else:
        result = await db.execute(
            select(DocumentParse)
            .order_by(DocumentParses.created_at.desc())
            .limit(limit)
            .offset(skip)
        ) 

    return result.scalars().all()


async def update_job(db: AsyncSession, job_id: int, data: JobUpdate) -> Job:
    job = await get_job(db,job_id)

    #extrait les colonnes données (on exclue les colonnes vides)
    update_data = data.model_dump(exclude_unset=True)
    #on insère les fields dans le doc afin de mettre à jour les données
    for field, value in update_data.items():
        setattr(job,field,value)
    
    await db.commit()
    await db.refresh(job)
    return job


async def delete_job(db: AsyncSession, job_id: int) -> None:
    job = await get_job(db, job_id)
    await db.delete(job)
    await db.commit()