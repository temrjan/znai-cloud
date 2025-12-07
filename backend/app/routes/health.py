"""Health check endpoint."""
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    Checks connectivity to:
    - PostgreSQL
    - Redis
    - Qdrant
    """
    # Check PostgreSQL
    postgres_ok = False
    try:
        await db.execute(text("SELECT 1"))
        postgres_ok = True
    except Exception:
        pass

    # Check Redis
    redis_ok = False
    try:
        redis_client = aioredis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        redis_ok = True
    except Exception:
        pass

    # Check Qdrant
    qdrant_ok = False
    try:
        qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        qdrant_client.get_collections()
        qdrant_ok = True
    except Exception:
        pass

    status_text = "healthy" if all([postgres_ok, redis_ok, qdrant_ok]) else "degraded"

    return HealthResponse(
        status=status_text,
        postgres=postgres_ok,
        redis=redis_ok,
        qdrant=qdrant_ok,
    )


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response

    from backend.app.utils.metrics import get_content_type, get_metrics

    return Response(
        content=get_metrics(),
        media_type=get_content_type()
    )
