"""Feedback routes for RAG quality tracking."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user
from backend.app.models.chat_message import ChatMessage
from backend.app.models.feedback import Feedback
from backend.app.models.user import User
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.app.utils.metrics import FEEDBACK_COUNT

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback on a RAG response.
    
    Users can rate responses as helpful or not helpful,
    with optional comments and categories.
    """
    # Verify message exists and belongs to user's session
    message_result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == feedback_data.message_id)
    )
    message = message_result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if feedback already exists for this message from this user
    existing_result = await db.execute(
        select(Feedback).where(
            Feedback.message_id == feedback_data.message_id,
            Feedback.user_id == current_user.id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Update existing feedback
        existing.is_helpful = feedback_data.is_helpful
        existing.comment = feedback_data.comment
        existing.category = feedback_data.category
        await db.commit()
        await db.refresh(existing)

        # Update metric
        rating = "positive" if feedback_data.is_helpful else "negative"
        FEEDBACK_COUNT.labels(rating=rating).inc()

        return FeedbackResponse.model_validate(existing)

    # Create new feedback
    feedback = Feedback(
        message_id=feedback_data.message_id,
        user_id=current_user.id,
        is_helpful=feedback_data.is_helpful,
        comment=feedback_data.comment,
        category=feedback_data.category,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Update metric
    rating = "positive" if feedback_data.is_helpful else "negative"
    FEEDBACK_COUNT.labels(rating=rating).inc()

    return FeedbackResponse.model_validate(feedback)


@router.get("/stats")
async def get_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get feedback statistics (admin only for now).
    """
    from sqlalchemy import func

    # Get total counts
    total_result = await db.execute(select(func.count(Feedback.id)))
    total = total_result.scalar() or 0

    positive_result = await db.execute(
        select(func.count(Feedback.id)).where(Feedback.is_helpful == True)
    )
    positive = positive_result.scalar() or 0

    negative_result = await db.execute(
        select(func.count(Feedback.id)).where(Feedback.is_helpful == False)
    )
    negative = negative_result.scalar() or 0

    # Calculate satisfaction rate
    satisfaction_rate = (positive / total * 100) if total > 0 else 0

    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "satisfaction_rate": round(satisfaction_rate, 2),
    }
