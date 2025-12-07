"""Document management routes."""
import hashlib
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user
from backend.app.models.document import Document, DocumentStatus
from backend.app.models.organization import Organization
from backend.app.models.quota import UserQuota
from backend.app.models.user import User
from backend.app.schemas.document import DocumentResponse
from backend.app.services.document_processor import document_processor
from backend.app.tasks.document_tasks import delete_document_task, index_document_task
from backend.app.utils.cache import SearchCache
from backend.app.utils.transliterate import transliterate_filename

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
}

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    visibility: str = Query(default="private", regex="^(private|organization)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and index a document.

    Visibility can be 'private' (personal) or 'organization' (shared with org members).
    """

    # Check file type by MIME and extension
    file_ext = Path(file.filename).suffix.lower()
    if file.content_type not in ALLOWED_TYPES and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Формат файла не поддерживается. Разрешены: PDF, TXT, MD",
        )

    # Validate visibility
    if visibility == "organization" and current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload organization documents without being in an organization",
        )

    # Transliterate Cyrillic filename to Latin for consistent storage
    original_filename = file.filename
    safe_filename = transliterate_filename(original_filename)

    # Calculate file hash
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    await file.seek(0)

    # Check for duplicate based on visibility
    if visibility == "organization":
        dup_result = await db.execute(
            select(Document).where(
                Document.organization_id == current_user.organization_id,
                Document.file_hash == file_hash,
            )
        )
    else:
        dup_result = await db.execute(
            select(Document).where(
                Document.uploaded_by_user_id == current_user.id,
                Document.visibility == "private",
                Document.file_hash == file_hash,
            )
        )

    if dup_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document has already been uploaded",
        )

    # Check quota based on visibility
    if visibility == "organization":
        # Check organization document quota
        org_result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = org_result.scalar_one()

        org_doc_count = await db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id == current_user.organization_id
            )
        )

        if org_doc_count >= organization.max_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization document limit reached ({organization.max_documents} documents)",
            )
    else:
        # Check personal document quota
        quota_result = await db.execute(
            select(UserQuota).where(UserQuota.user_id == current_user.id)
        )
        quota = quota_result.scalar_one()

        # Count personal documents
        personal_doc_count = await db.scalar(
            select(func.count(Document.id)).where(
                Document.uploaded_by_user_id == current_user.id,
                Document.visibility == "private"
            )
        )

        # Use personal quota if user is in org (hybrid mode), otherwise use general quota
        max_docs = quota.personal_max_documents if current_user.organization_id else quota.max_documents
        if personal_doc_count >= max_docs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Personal document limit reached ({max_docs} documents)",
            )

    # Save file with transliterated filename
    file_path = UPLOAD_DIR / f"{current_user.id}_{file_hash}_{safe_filename}"
    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create document record (store transliterated filename)
    document = Document(
        uploaded_by_user_id=current_user.id,
        organization_id=current_user.organization_id if visibility == "organization" else None,
        filename=safe_filename,
        file_path=str(file_path),
        file_hash=file_hash,
        file_size=len(file_content),
        mime_type=file.content_type,
        visibility=visibility,
        status=DocumentStatus.PROCESSING,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Queue async indexing task
    index_document_task.delay(
        document_id=document.id,
        document_uuid=str(document.id),
        user_id=current_user.id,
        filename=document.filename,
        file_path=document.file_path,
        mime_type=document.mime_type,
        organization_id=document.organization_id,
        visibility=document.visibility,
    )
    logger.info(f"Queued indexing task for document {document.id}")

    return document


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    scope: str | None = Query(default="all", regex="^(all|organization|private)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List documents accessible to the user.

    Scopes:
    - 'all': Both organization and personal documents (default, hybrid mode)
    - 'organization': Only organization documents
    - 'private': Only personal documents
    """
    conditions = []

    if scope == "organization":
        if current_user.organization_id is None:
            return []
        conditions.append(Document.organization_id == current_user.organization_id)

    elif scope == "private":
        conditions.append(
            (Document.uploaded_by_user_id == current_user.id) &
            (Document.visibility == "private")
        )

    else:  # scope == "all"
        # Hybrid mode: show org docs + personal docs
        if current_user.organization_id:
            conditions.append(
                or_(
                    Document.organization_id == current_user.organization_id,
                    (Document.uploaded_by_user_id == current_user.id) &
                    (Document.visibility == "private")
                )
            )
        else:
            # Personal mode: only personal documents
            conditions.append(
                (Document.uploaded_by_user_id == current_user.id) &
                (Document.visibility == "private")
            )

    query = select(Document).where(*conditions).order_by(Document.uploaded_at.desc())
    result = await db.execute(query)
    documents = result.scalars().all()

    return documents


@router.post("/{document_id}/index", response_model=DocumentResponse)
async def index_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Index an uploaded document."""
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check access: user must own it or be in same organization
    has_access = False
    if document.visibility == "private":
        has_access = (document.uploaded_by_user_id == current_user.id)
    elif document.visibility == "organization":
        has_access = (document.organization_id == current_user.organization_id)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this document",
        )

    if document.status == DocumentStatus.INDEXED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document already indexed",
        )

    # Process and index
    try:
        document.status = DocumentStatus.PROCESSING
        await db.commit()

        # Queue async indexing task
        index_document_task.delay(
            document_id=document.id,
            document_uuid=str(document.id),
            user_id=current_user.id,
            filename=document.filename,
            file_path=document.file_path,
            mime_type=document.mime_type,
            organization_id=document.organization_id,
            visibility=document.visibility,
        )
        logger.info(f"Queued indexing task for document {document_id}")

        # Return immediately - document will be indexed in background
        # Status remains PROCESSING until Celery task completes

    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}",
        )

    await db.commit()
    await db.refresh(document)

    # Queue async indexing task
    index_document_task.delay(
        document_id=document.id,
        document_uuid=str(document.id),
        user_id=current_user.id,
        filename=document.filename,
        file_path=document.file_path,
        mime_type=document.mime_type,
        organization_id=document.organization_id,
        visibility=document.visibility,
    )
    logger.info(f"Queued indexing task for document {document.id}")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document.

    Permission rules:
    - Users can delete their own personal documents
    - Organization admins/owners can delete any organization document
    - Organization members can only delete their own organization documents
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permissions
    can_delete = False

    if document.visibility == "private":
        # Personal document: only owner can delete
        can_delete = (document.uploaded_by_user_id == current_user.id)
    else:
        # Organization document
        if document.organization_id == current_user.organization_id:
            # Same organization
            if current_user.is_org_admin_or_owner():
                # Admins/owners can delete any org document
                can_delete = True
            elif document.uploaded_by_user_id == current_user.id:
                # Members can delete their own documents
                can_delete = True

    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document",
        )

    # Save IDs for cache invalidation
    user_id = document.uploaded_by_user_id
    org_id = document.organization_id

    # Delete from Qdrant (with filename fallback for legacy documents)
    try:
        document_processor.delete_document(str(document.id), filename=document.filename)
    except Exception as e:
        logger.warning(f"Failed to delete from Qdrant: {e}")

    # Delete file
    try:
        Path(document.file_path).unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"Failed to delete file: {e}")

    # Delete from database
    await db.delete(document)
    await db.commit()

    # Invalidate search cache after deleting document
    SearchCache.invalidate_user(user_id)
    if org_id:
        SearchCache.invalidate_org(org_id)
    logger.info(f"Cache invalidated after deleting document {document_id}")
