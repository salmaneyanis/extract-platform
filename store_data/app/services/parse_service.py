from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import DocumentParse
from app.services.exceptions import DocumentParseNotFoundError, DatabaseError
from app.schemas.document_schemas import DocumentParseCreate

async def create_parse(db: AsyncSession, data: DocumentParseCreate) -> DocumentParse:
    """  """
    doc = DocumentParse(
        doc_id=data.doc_id,
        representation_type=data.representation_type,
        content_json=data.content_json,
        content_text=data.content_text,
    )

    db.add(doc)

    await db.commit()
    await db.refresh(doc)
    return doc



async def get_parse(db: AsyncSession, parse_id: int) -> DocumentParse | None:
    result = await db.execute(select(DocumentParse).where(DocumentParse.parse_id == parse_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise DocumentParseNotFoundError(f"DocumentParse {parse_id} introuvable")

    return document

async def list_parses(db: AsyncSession, doc_id: int | None = None ,skip: int = 0, limit: int = 100) -> list[DocumentParse]:
    stmt = select(DocumentParse).order_by(DocumentParse.created_at.desc()).limit(limit).offset(skip)
    if doc_id is not None:
        stmt = stmt.where(DocumentParse.doc_id == doc_id)
    result = await db.execute(stmt)
    return result.scalars().all()

   



    


async def delete_parse(db: AsyncSession, parse_id: int) -> None:
    parse = await get_parse(db, parse_id)
    await db.delete(parse)
    await db.commit()
    return None


