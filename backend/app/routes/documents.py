"""Document management routes."""
import hashlib
import shutil
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document, DocumentStatus
from backend.app.models.quota import UserQuota
from backend.app.schemas.document import DocumentResponse
from backend.app.middleware.auth import get_current_user
from backend.app.services.document_processor import document_processor
from backend.app.config import settings


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("/home/temrjan/ai-avangard/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".doc", ".docx"}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and index a document."""

    # Check file type by MIME and extension
    file_ext = Path(file.filename).suffix.lower()
    if file.content_type not in ALLOWED_TYPES and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: PDF, TXT, MD, DOC, DOCX",
        )

    # Check quota
    quota_result = await db.execute(
        select(UserQuota).where(UserQuota.user_id == current_user.id)
    )
    quota = quota_result.scalar_one()

    if quota.current_documents >= quota.max_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document limit reached ({quota.max_documents} documents)",
        )

    # Calculate file hash
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    await file.seek(0)

    # Check for duplicate
    dup_result = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.file_hash == file_hash,
        )
    )
    if dup_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document has already been uploaded",
        )

    # Save file
    file_path = UPLOAD_DIR / f"{current_user.id}_{file_hash}_{file.filename}"
    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_hash=file_hash,
        file_size=len(file_content),
        mime_type=file.content_type,
        status=DocumentStatus.PROCESSING,
    )

    db.add(document)
    await db.flush()

    # Update quota
    quota.current_documents += 1

    await db.commit()
    await db.refresh(document)

    return document


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's documents."""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
    )
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
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
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

        chunks_count = document_processor.index_document(
            document_id=document.id,
            user_id=current_user.id,
            filename=document.filename,
            file_path=Path(document.file_path),
            mime_type=document.mime_type,
        )

        document.status = DocumentStatus.INDEXED
        document.chunks_count = chunks_count

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
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete from Qdrant
    try:
        document_processor.delete_document(str(document.id))
    except Exception as e:
        print(f"Warning: Failed to delete from Qdrant: {e}")

    # Delete file
    try:
        Path(document.file_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: Failed to delete file: {e}")

    # Update quota
    quota_result = await db.execute(
        select(UserQuota).where(UserQuota.user_id == current_user.id)
    )
    quota = quota_result.scalar_one()
    quota.current_documents = max(0, quota.current_documents - 1)

    # Delete from database
    await db.delete(document)
    await db.commit()
