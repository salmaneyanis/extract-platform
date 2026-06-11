from fastapi import APIRouter, HTTPException, Query
from app.services.orchestration_service import (
    get_parse, list_parses, delete_parse
)

router = APIRouter(prefix="/parses", tags=["parses"])


@router.get("/{parse_id}", status_code=200)
async def get_parse_route(parse_id: int):
    """Get single parse."""
    try:
        parse = await get_parse(parse_id)
        return parse
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", status_code=200)
async def list_parses_route(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=10000)):
    """List all parses."""
    try:
        parses = await list_parses(skip, limit)
        return parses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{parse_id}", status_code=204)
async def delete_parse_route(parse_id: int):
    """Delete parse."""
    try:
        await delete_parse(parse_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
