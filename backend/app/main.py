"""
AI-Avangard FastAPI Application
Multi-tenant RAG platform for personal knowledge bases
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.routes import (
    admin,
    auth,
    chat,
    chat_sessions,
    documents,
    feedback,
    health,
    invites,
    organizations,
    quota,
    telegram_webhook,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 Database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"🔴 Redis: {settings.redis_host}:{settings.redis_port}")
    print(f"🔷 Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging."""
    logger.error(f"Validation error on {request.url}: {exc.errors()}")
    print(f"VALIDATION ERROR: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(quota.router)
app.include_router(admin.router)
app.include_router(organizations.router)
app.include_router(chat_sessions.router)
app.include_router(feedback.router)
app.include_router(invites.router)
app.include_router(telegram_webhook.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }
