"""Chat/RAG routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import OpenAI

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.quota import UserQuota
from backend.app.models.query_log import QueryLog
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.middleware.auth import get_current_user
from backend.app.services.document_processor import document_processor
from backend.app.config import settings


router = APIRouter(prefix="/chat", tags=["Chat"])

openai_client = OpenAI(api_key=settings.openai_api_key)


@router.post("", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process RAG query.

    Searches user's documents and generates answer using OpenAI.
    Applies organization settings if user is in an organization.
    """

    # Load organization settings if user is in organization
    org_settings = None
    if current_user.organization_id:
        settings_result = await db.execute(
            select(OrganizationSettings).where(
                OrganizationSettings.organization_id == current_user.organization_id
            )
        )
        org_settings = settings_result.scalar_one_or_none()

    # Check quota
    quota_result = await db.execute(
        select(UserQuota).where(UserQuota.user_id == current_user.id)
    )
    quota = quota_result.scalar_one()

    # Reset daily counter if needed
    from datetime import date
    if quota.last_query_date != date.today():
        quota.queries_today = 0
        quota.last_query_date = date.today()

    if quota.queries_today >= quota.max_queries_daily:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily query limit reached ({quota.max_queries_daily} queries per day)",
        )

    # Determine search parameters (use org settings if available)
    search_limit = org_settings.search_top_k if org_settings and org_settings.search_top_k else 5
    score_threshold = org_settings.search_similarity_threshold if org_settings and org_settings.search_similarity_threshold else 0.35

    # Search for relevant chunks
    search_results = document_processor.search(
        user_id=current_user.id,
        query=request.question,
        limit=search_limit,
        score_threshold=score_threshold,
        organization_id=current_user.organization_id,
        search_scope=request.search_scope,
    )

    if not search_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No relevant information found. Please upload documents first.",
        )

    # Build context from search results
    context = "\n\n".join([
        f"From {result['filename']}:\n{result['text']}"
        for result in search_results
    ])

    # Apply custom terminology if available
    if org_settings and org_settings.custom_terminology:
        for term, expansion in org_settings.custom_terminology.items():
            context = context.replace(term, f"{term} ({expansion})")

    # Determine OpenAI parameters (use org settings if available)
    system_prompt = org_settings.custom_system_prompt if org_settings and org_settings.custom_system_prompt else (
        "Ты - помощник, который отвечает на вопросы на основе предоставленного контекста. "
        "Давай подробные, развёрнутые ответы, используя всю доступную информацию из контекста. "
        "Если в контексте есть номера сур и аятов (например [2:3]), обязательно включай их в ответ. "
        "Используй только информацию из контекста. Если ответа нет в контексте, так и скажи."
    )

    temperature = org_settings.custom_temperature if org_settings and org_settings.custom_temperature is not None else 0.5
    max_tokens = org_settings.custom_max_tokens if org_settings and org_settings.custom_max_tokens else 2500

    # Generate answer with OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Контекст:\n{context}\n\nВопрос: {request.question}"
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}",
        )

    # Update quota
    quota.queries_today += 1

    # Extract unique sources
    sources = list(set(result['filename'] for result in search_results))

    # Log query
    query_log = QueryLog(
        user_id=current_user.id,
        query_text=request.question,
        sources_count=len(sources),
        organization_id=current_user.organization_id,
        search_mode=request.search_scope,
    )
    db.add(query_log)

    await db.commit()

    return ChatResponse(
        answer=answer,
        sources=sources,
    )
