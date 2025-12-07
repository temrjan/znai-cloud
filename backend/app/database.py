"""Database connection and session management."""
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.config import settings

# Async engine for FastAPI
if settings.debug:
    engine = create_async_engine(
        settings.database_url,
        echo=True,
        poolclass=NullPool,
    )
else:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=settings.postgres_pool_size,
        max_overflow=settings.postgres_max_overflow,
    )

# Async session factory for FastAPI
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Sync engine for Celery tasks
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=0,
)

# Sync session factory for Celery
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
