from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.document_schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
)
from app.services.persistence_service import (
    create_document,
    get_document,
    list_documents,
    update_document,
    delete_document,
    DocumentNotFoundError,
    DatabaseError,
)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", status_code=201, response_model=DocumentResponse)
async def create( data: DocumentCreate,db: AsyncSession = Depends(get_db)):
    return await create_document(db, data)

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get(doc_id: int, db: AsyncSession = Depends(get_db) ):
    try:
        return await get_document(db,doc_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404,detail=str(e))

@router.get("", response_model=list[DocumentResponse])
async def get_all(skip: int = Query(0,ge=0), limit: int = Query(100, ge=1, le=10000) ,db: AsyncSession = Depends(get_db)):
    return await list_documents(db,skip,limit)


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update(doc_id: int, data: DocumentUpdate, db: AsyncSession = Depends(get_db)):
    return await update_document(db, doc_id, data)

@router.delete("/{doc_id}", status_code=204) 
async def delete(doc_id: int, db: AsyncSession = Depends(get_db)):
    await delete_document(db, doc_id)


 