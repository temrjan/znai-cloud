"""Celery tasks for document processing."""
import logging
from pathlib import Path

from backend.app.celery_app import celery_app
from backend.app.database import SessionLocal
from backend.app.models.document import Document, DocumentStatus
from backend.app.services.document_processor import document_processor
from backend.app.utils.cache import SearchCache

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def index_document_task(
    self,
    document_id: int,
    document_uuid: str,
    user_id: int,
    filename: str,
    file_path: str,
    mime_type: str,
    organization_id: int | None = None,
    visibility: str = "private",
):
    """
    Async task to index a document.

    Args:
        document_id: Database ID of the document
        document_uuid: UUID of the document for Qdrant
        user_id: User who uploaded the document
        filename: Original filename
        file_path: Path to the uploaded file
        mime_type: MIME type of the file
        organization_id: Organization ID if applicable
        visibility: 'private' or 'organization'
    """
    logger.info(f"Starting indexing task for document {document_id}: {filename}")

    try:
        # Index the document
        chunks_count = document_processor.index_document(
            document_id=document_uuid,
            user_id=user_id,
            filename=filename,
            file_path=Path(file_path),
            mime_type=mime_type,
            organization_id=organization_id,
            visibility=visibility,
        )

        # Update document status in database (sync session for Celery)
        with SessionLocal() as db:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.INDEXED
                document.chunks_count = chunks_count
                db.commit()
                logger.info(f"Document {document_id} indexed successfully: {chunks_count} chunks")

        # Invalidate search cache
        SearchCache.invalidate_user(user_id)
        if organization_id:
            SearchCache.invalidate_org(organization_id)

        return {
            "status": "success",
            "document_id": document_id,
            "chunks_count": chunks_count,
        }

    except Exception as e:
        logger.error(f"Error indexing document {document_id}: {e}")

        # Update document status to failed
        try:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = DocumentStatus.FAILED
                    document.error_message = str(e)[:500]
                    db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update document status: {db_error}")

        # Retry the task
        raise self.retry(exc=e)


@celery_app.task(bind=True)
def delete_document_task(self, document_uuid: str, user_id: int = None, organization_id: int = None):
    """
    Async task to delete a document from the index.

    Args:
        document_uuid: UUID of the document to delete
        user_id: User ID for cache invalidation
        organization_id: Org ID for cache invalidation
    """
    logger.info(f"Starting delete task for document {document_uuid}")

    try:
        document_processor.delete_document(document_uuid)

        # Invalidate cache
        if user_id:
            SearchCache.invalidate_user(user_id)
        if organization_id:
            SearchCache.invalidate_org(organization_id)

        logger.info(f"Document {document_uuid} deleted from index")
        return {"status": "success", "document_uuid": document_uuid}

    except Exception as e:
        logger.error(f"Error deleting document {document_uuid}: {e}")
        return {"status": "error", "error": str(e)}
