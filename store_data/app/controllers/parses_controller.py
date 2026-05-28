from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.document_schemas import (
    DocumentParseCreate,
    DocumentParseResponse,
)
from app.services.persistence_service import (
    create_parse,
    get_parse,
    list_parse,
    delete_parse,
)

from app.services.exceptions(
    DatabaseError,
    ParseNotFoundError,
)

router = APIRouter(prefix="/parses", tags=["parses"])

@router.post("", status_code=201, response_model=DocumentParseResponse)
async def create( data: DocumentParseCreate,db: AsyncSession = Depends(get_db)):
    return await create_parse(db, data)

@router.get("/{parse_id}", response_model=DocumentParseResponse)
async def get(parse_id: int, db: AsyncSession = Depends(get_db) ):
    try:
        return await get_parse(db,parse_id)
    except ParseNotFoundError as e:
        raise HTTPException(status_code=404,detail=str(e))

@router.get("", response_model=list[ParseResponse])
async def get_all(skip: int = Query(0,ge=0), limit: int = Query(100, ge=1, le=10000) ,db: AsyncSession = Depends(get_db)):
    return await list_parses(db,skip,limit)




@router.delete("/{parse_id}", status_code=204) 
async def delete(parse_id: int, db: AsyncSession = Depends(get_db)):
    await delete_parse(db, parse_id)


 