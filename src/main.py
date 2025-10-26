"""
Al-Muwatta (الموطأ) - Maliki Fiqh Assistant API

Main FastAPI application specialized in Maliki jurisprudence with
RAG-enhanced responses using Google Gemini and Qdrant vector database.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config import settings
from .routers import (
    hadith_router,
    quran_router,
    prayer_times_router,
    ai_router,
    upload_router,
    settings_router,
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
    logger.info(f"RAG System: Maliki Fiqh with Qdrant Vector DB")
    yield
    # Shutdown
    logger.info("Shutting down Al-Muwatta")


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "*"  # Allow all in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred",
        },
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
async def root() -> Dict[str, str]:
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
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


# API info endpoint
@app.get("/api/v1/info", tags=["Info"])
async def api_info() -> Dict[str, Any]:
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

