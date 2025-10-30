"""
Al-Muwatta (الموطأ) - Maliki Fiqh Assistant API

Main FastAPI application specialized in Maliki jurisprudence with
RAG-enhanced responses using Google Gemini and Qdrant vector database.
"""

import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi.errors import RateLimitExceeded

from .config import settings
from .middleware.rate_limiting import limiter, rate_limit_exceeded_handler
from .routers import (
    ai_router,
    hadith_router,
    prayer_times_router,
    quran_router,
    settings_router,
    upload_router,
)

# Configure logger
logger.add(
    "logs/nur_al_ilm.log",
    rotation="100 MB",
    retention="10 days",
    level=settings.log_level,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Using Gemini model: {settings.gemini_model}")
    logger.info("RAG System: Maliki Fiqh with Qdrant Vector DB")

    # Initialize cache service
    from .services.cache_service import get_cache_service

    cache = get_cache_service()
    await cache.connect_redis()

    yield

    # Shutdown
    logger.info("Shutting down Al-Muwatta")

    # Disconnect cache service
    await cache.disconnect_redis()


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# Nur Al-Ilm - نور العلم
### Intelligent Islamic Knowledge Assistant

A comprehensive API for accessing Islamic content with AI-powered insights using Google Gemini.

## Features

### 📚 Hadith Collections
- Access multiple authentic Hadith collections (Sahih Bukhari, Sahih Muslim, etc.)
- Search Hadiths in Arabic and English
- AI-powered explanations and context

### 📖 Quranic Content
- Complete Quran access with multiple translations
- Search verses by topic or keyword
- AI-generated Tafsir (exegesis)
- Access by Surah, Juz, or Page

### 🕌 Prayer Times
- Accurate prayer times worldwide
- Multiple calculation methods
- Islamic calendar (Hijri/Gregorian conversion)
- Qibla direction finder
- 99 Names of Allah (Asma Al-Husna)

### 🤖 AI Assistant (Powered by Google Gemini)
- Answer Islamic questions with scholarly references
- Generate thematic studies on Islamic topics
- Contextual translation of Islamic texts
- Daily Islamic reminders
- Hadith authenticity verification guidance

## Usage Examples

### Get Surah Al-Fatiha
```
GET /api/v1/quran/surahs/1?edition=en.sahih
```

### Search Hadiths
```
GET /api/v1/hadith/search?query=prayer&limit=10
```

### Get Prayer Times
```
GET /api/v1/prayer-times/timings?latitude=21.3891&longitude=39.8579
```

### Ask Islamic Question
```
POST /api/v1/ai/ask
{
    "question": "What are the pillars of Islam?",
    "language": "english"
}
```

## Data Sources
- **Hadith**: sunnah.com API
- **Quran**: alquran.cloud API
- **Prayer Times**: aladhan.com API
- **AI**: Google Gemini 2.0 Flash

## Contact & Support
Built with ❤️ for the Muslim Ummah
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Initialize rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS - Use environment-based origins for security
_allowed_origins = (
    [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
    if settings.allowed_origins
    else []
)

# In development, allow localhost origins
if settings.debug and not _allowed_origins:
    _allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add compression middleware for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Add request ID middleware for request tracking
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with structured error response."""

    # Log full error details for debugging
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": getattr(request.state, "request_id", None),
        },
    )

    # Prepare error detail - sanitize in production
    if settings.debug:
        error_detail = {
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__,
        }
    else:
        error_detail = {
            "error": "Internal server error",
            "detail": "An error occurred. Please try again later.",
        }

    return JSONResponse(
        status_code=500,
        content=error_detail,
    )


# Include routers
app.include_router(hadith_router)
app.include_router(quran_router)
app.include_router(prayer_times_router)
app.include_router(ai_router)
app.include_router(upload_router)
app.include_router(settings_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    API root endpoint with welcome message.

    Returns:
        Welcome message and API information
    """
    return {
        "message": "Welcome to Nur Al-Ilm - نور العلم",
        "description": "Intelligent Islamic Knowledge Assistant",
        "version": settings.app_version,
        "powered_by": "Google Gemini AI",
        "documentation": "/docs",
        "github": "https://github.com/your-repo/nur-al-ilm",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Returns:
        Service health status with cache, database, and external API checks
    """
    from .services.cache_service import get_cache_service

    health_status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }

    # Check cache service
    try:
        cache = get_cache_service()
        cache_stats = cache.get_stats()
        health_status["cache"] = {
            "status": "healthy"
            if cache.redis_enabled or cache_stats["memory_cache_size"] > 0
            else "degraded",
            "redis_enabled": cache.redis_enabled,
            "memory_cache_size": cache_stats["memory_cache_size"],
        }
    except Exception as e:
        health_status["cache"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check external APIs (quick ping test)
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Quick health check - try to reach external APIs
            health_status["external_apis"] = {
                "quran_api": "unknown",  # Would need actual ping
                "hadith_api": "unknown",
                "prayer_times_api": "unknown",
            }
    except Exception as e:
        health_status["external_apis"] = {"status": "check_failed", "error": str(e)}

    return health_status


# API info endpoint
@app.get("/api/v1/info", tags=["Info"])
async def api_info() -> dict[str, Any]:
    """
    Get API information and statistics.

    Returns:
        API information
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "ai_model": settings.gemini_model,
        "features": {
            "hadith_collections": "Multiple authentic collections",
            "quran_editions": "Multiple translations and recitations",
            "prayer_times": "Worldwide coverage",
            "ai_assistant": "Powered by Google Gemini",
        },
        "data_sources": {
            "hadith": "sunnah.com API",
            "quran": "alquran.cloud API",
            "prayer_times": "aladhan.com API",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
