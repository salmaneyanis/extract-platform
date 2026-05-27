from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Document
from app.schemas.document_schemas import DocumentParseCreate

class DocumentParseNotFoundError(Exception):
    """Levée quand un document n'existe pas en BDD."""
    pass


class DatabaseError(Exception):
    """Erreur générique de base de données."""
    pass

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

async def list_parses(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[DocumentParse]:
    result = await db.execute(
        select(DocumentParse)
        .order_by(DocumentParses.created_at.desc())
        .limit(limit)
        .offset(skip)
    ) 
    return result.scalars().all()


async def delete_parse(db: AsyncSession, parse_id: int) -> None:
    result = await db.execute(select(DocumentParse).filter(DocumentParse.parse_id == parse_id))
    db_item = result.scalar_one_or_none()
    await db.delete(db_item)
    await db.commit()
    return None

