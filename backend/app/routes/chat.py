"""Chat/RAG routes with reranking and caching."""
import json
import logging
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.quota import UserQuota
from backend.app.models.query_log import QueryLog
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.models.chat_session import ChatSession
from backend.app.models.chat_message import ChatMessage, MessageRole
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.middleware.auth import get_current_user
from backend.app.services.document_processor import document_processor
from backend.app.services.chat_service import chat_service, DEFAULT_SYSTEM_PROMPT, MAX_CONTEXT_MESSAGES
from backend.app.utils.cache import SearchCache
from backend.app.config import settings


router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

NO_RESULTS_MESSAGE = (
    "К сожалению, я не нашёл релевантной информации по вашему вопросу "
    "в загруженных документах.\n\nПопробуйте:\n"
    "1. Переформулировать вопрос более конкретно\n"
    "2. Использовать другие ключевые слова\n"
    "3. Загрузить дополнительные документы по этой теме"
)


async def check_quota(db: AsyncSession, user_id: int) -> UserQuota:
    """Check user quota and raise exception if exceeded."""
    result = await db.execute(select(UserQuota).where(UserQuota.user_id == user_id))
    quota = result.scalar_one()
    
    if quota.last_query_date != date.today():
        quota.queries_today = 0
        quota.last_query_date = date.today()
    
    if quota.queries_today >= quota.max_queries_daily:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily query limit reached ({quota.max_queries_daily} queries per day)",
        )
    return quota


async def get_or_create_session(
    db: AsyncSession, user_id: int, session_id: int | None, question: str
) -> tuple[ChatSession, list[ChatMessage]]:
    """Get existing session or create new one."""
    history_messages = []
    
    if session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        history_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(MAX_CONTEXT_MESSAGES)
        )
        history_messages = list(reversed(history_result.scalars().all()))
        return session, history_messages
    
    # Create new session (with cleanup if needed)
    count_result = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)
    )
    if count_result.scalar() >= ChatSession.MAX_SESSIONS_PER_USER:
        oldest_result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.asc())
            .limit(1)
        )
        oldest = oldest_result.scalar_one_or_none()
        if oldest:
            await db.delete(oldest)
    
    title = question[:50] + "..." if len(question) > 50 else question
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    return session, history_messages


async def get_org_settings(db: AsyncSession, org_id: int | None) -> OrganizationSettings | None:
    """Get organization settings if user is in an organization."""
    if not org_id:
        return None
    result = await db.execute(
        select(OrganizationSettings).where(OrganizationSettings.organization_id == org_id)
    )
    return result.scalar_one_or_none()


def search_documents(user_id: int, question: str, org_id: int | None, search_scope: str) -> list:
    """Search documents with caching and reranking."""
    cached = SearchCache.get(
        user_id=user_id, query=question, org_id=org_id, scope=search_scope
    )
    if cached is not None:
        return cached
    
    results = document_processor.search(
        user_id=user_id,
        query=question,
        limit=25,
        score_threshold=0.35,
        organization_id=org_id,
        search_scope=search_scope,
        use_reranking=True,
        rerank_top_n=5,
    )
    
    SearchCache.set(
        user_id=user_id, query=question, org_id=org_id, scope=search_scope, results=results
    )
    
    if results:
        scores = [r.get("rerank_score", r.get("score", 0)) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        logger.info(
            f"RAG Search: query=\"{question[:50]}...\", results={len(results)}, "
            f"avg_score={avg_score:.3f}, top_score={max(scores) if scores else 0:.3f}"
        )
    
    return results


@router.post("", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process RAG query with reranking, caching, and retry logic."""
    quota = await check_quota(db, current_user.id)
    session, history_messages = await get_or_create_session(
        db, current_user.id, request.session_id, request.question
    )
    org_settings = await get_org_settings(db, current_user.organization_id)
    
    search_results = search_documents(
        current_user.id, request.question, current_user.organization_id, request.search_scope
    )
    
    # No results found
    if not search_results:
        user_msg = ChatMessage(session_id=session.id, role=MessageRole.USER, content=request.question)
        assistant_msg = ChatMessage(
            session_id=session.id, role=MessageRole.ASSISTANT,
            content=NO_RESULTS_MESSAGE, sources=json.dumps([])
        )
        db.add_all([user_msg, assistant_msg])
        quota.queries_today += 1
        await db.commit()
        return ChatResponse(answer=NO_RESULTS_MESSAGE, sources=[], session_id=session.id)
    
    # Build context and messages
    context = chat_service.build_context(
        search_results,
        org_settings.custom_terminology if org_settings else None
    )
    
    system_prompt = (
        org_settings.custom_system_prompt if org_settings and org_settings.custom_system_prompt
        else DEFAULT_SYSTEM_PROMPT
    )
    
    messages = chat_service.build_messages(system_prompt, history_messages, request.question, context)
    
    # Get model parameters
    model_name = (
        org_settings.custom_model if org_settings and org_settings.custom_model
        else settings.openai_llm_model
    )
    temperature = (
        org_settings.custom_temperature if org_settings and org_settings.custom_temperature is not None
        else 0.5
    )
    max_tokens = (
        org_settings.custom_max_tokens if org_settings and org_settings.custom_max_tokens
        else 4096
    )
    
    # Generate response
    try:
        answer = chat_service.generate_response(
            messages=messages, model=model_name, temperature=temperature, max_tokens=max_tokens
        )
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail="Сервис временно недоступен. Попробуйте позже.")
    
    # Save messages and update state
    sources = list(set(r['filename'] for r in search_results))
    
    user_msg = ChatMessage(session_id=session.id, role=MessageRole.USER, content=request.question)
    assistant_msg = ChatMessage(
        session_id=session.id, role=MessageRole.ASSISTANT, content=answer, sources=json.dumps(sources)
    )
    db.add_all([user_msg, assistant_msg])
    
    session.updated_at = datetime.utcnow()
    quota.queries_today += 1
    
    query_log = QueryLog(
        user_id=current_user.id,
        query_text=request.question,
        sources_count=len(sources),
        organization_id=current_user.organization_id,
        search_mode=request.search_scope,
    )
    db.add(query_log)
    
    await db.commit()
    return ChatResponse(answer=answer, sources=sources, session_id=session.id)
