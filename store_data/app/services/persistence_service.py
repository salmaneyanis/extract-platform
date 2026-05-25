from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Document
from app.schemas.document_schemas import DocumentCreate, DocumentUpdate

class DocumentNotFoundError(Exception):
    """Levée quand un document n'existe pas en BDD."""
    pass


class DatabaseError(Exception):
    """Erreur générique de base de données."""
    pass

async def create_document(db: AsyncSession, data: DocumentCreate) -> Document:
    """  """
    doc = Document(
        file_name=data.file_name,
        category=data.category,
    )

    db.add(doc)

    await db.commit()
    await db.refresh(doc)
    return doc



async def get_document(db: AsyncSession, doc_id: int) -> Document | None:
    result = await db.execute(select(Document).where(Document.doc_id == doc_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise DocumentNotFoundError(f"Document {doc_id} introuvable")

    return document

async def list_documents(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Document]:
    result = await db.execute(
        select(Document)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(skip)
    ) 
    return result.scalars().all()

async def update_document(db: AsyncSession, doc_id: int, data: DocumentUpdate) -> Document:
    doc = await get_document(db,doc_id)

    #extrait les colonnes données (on exclue les colonnes vides)
    update_data = data.model_dump(exclude_unset=True)
    #on insère les fields dans le doc afin de mettre à jour les données
    for field, value in update_data.items():
        setattr(doc,field,value)
    
    await db.commit()
    await db.refresh(doc)
    return doc
    

async def delete_document(db: AsyncSession, doc_id: int) -> None:
    result = await db.execute(select(Document).filter(Document.doc_id == doc_id))
    db_item = result.scalar_one_or_none()
    await db.delete(db_item)
    await db.commit()
    return None