"""Chat sessions routes."""
import json
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user
from backend.app.models.chat_message import ChatMessage, MessageRole
from backend.app.models.chat_session import ChatSession
from backend.app.models.user import User
from backend.app.schemas.chat_session import (
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatSessionUpdate,
    ChatSessionWithMessages,
)

router = APIRouter(prefix="/chat-sessions", tags=["Chat Sessions"])


@router.get("", response_model=ChatSessionListResponse)
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's chat sessions (max 20, ordered by updated_at desc)."""
    # Get sessions with message count
    result = await db.execute(
        select(
            ChatSession,
            func.count(ChatMessage.id).label("message_count")
        )
        .outerjoin(ChatMessage)
        .where(ChatSession.user_id == current_user.id)
        .group_by(ChatSession.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(ChatSession.MAX_SESSIONS_PER_USER)
    )

    sessions = []
    for row in result.all():
        session = row[0]
        message_count = row[1]
        sessions.append(ChatSessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=message_count
        ))

    return ChatSessionListResponse(sessions=sessions, total=len(sessions))


@router.post("", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    # Check session limit - delete oldest if exceeded
    count_result = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.user_id == current_user.id)
    )
    session_count = count_result.scalar()

    if session_count >= ChatSession.MAX_SESSIONS_PER_USER:
        # Delete oldest session
        oldest_result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == current_user.id)
            .order_by(ChatSession.updated_at.asc())
            .limit(1)
        )
        oldest_session = oldest_result.scalar_one_or_none()
        if oldest_session:
            await db.delete(oldest_session)

    # Create new session
    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title or "Новый чат"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )


@router.get("/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a chat session with all messages."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Get messages
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = messages_result.scalars().all()

    return ChatSessionWithMessages(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(messages),
        messages=[
            ChatMessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                sources=json.loads(msg.sources) if msg.sources else None,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.patch("/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: int,
    session_data: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update chat session title."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    session.title = session_data.title
    await db.commit()
    await db.refresh(session)

    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    await db.delete(session)
    await db.commit()


async def cleanup_old_sessions(db: AsyncSession):
    """Cleanup sessions older than retention period. Run via cron/scheduled task."""
    cutoff_date = datetime.utcnow() - timedelta(days=ChatSession.SESSION_RETENTION_DAYS)
    await db.execute(
        delete(ChatSession).where(ChatSession.updated_at < cutoff_date)
    )
    await db.commit()
