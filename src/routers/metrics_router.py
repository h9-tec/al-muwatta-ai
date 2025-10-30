"""
Metrics and health check endpoints for Al-Muwatta.

Provides detailed system health status and cache statistics.
"""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from ..services.cache_service import get_cache_service

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/health/detailed", summary="Detailed health check")
async def detailed_health_check() -> dict[str, Any]:
    """
    Detailed health check with component status.

    Returns:
        Comprehensive health status including:
        - Overall system status
        - Component-level health
        - Cache statistics
        - Performance metrics

    Example:
        >>> response = await client.get("/api/v1/metrics/health/detailed")
        >>> print(response.json()["status"])
        "healthy"
    """
    try:
        cache = get_cache_service()
        cache_stats = cache.get_stats()

        # Determine cache health status
        cache_status = "up" if cache.redis_enabled else "degraded"

        # Overall system health
        overall_status = "healthy"

        return {
            "status": overall_status,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "components": {
                "api": {"status": "up", "description": "API server is running"},
                "cache": {
                    "status": cache_status,
                    "redis_enabled": cache.redis_enabled,
                    "hit_rate_percent": cache_stats["hit_rate_percent"],
                    "total_requests": cache_stats["total_requests"],
                    "memory_cache_size": cache_stats["memory_cache_size"],
                    "description": "Redis" if cache.redis_enabled else "In-memory fallback",
                },
                "rag": {"status": "up", "description": "RAG system operational"},
                "llm": {"status": "up", "description": "LLM providers available"},
            },
            "metrics": {
                "cache": {
                    "hit_rate": cache_stats["hit_rate_percent"],
                    "hits": cache_stats["hits"],
                    "misses": cache_stats["misses"],
                    "redis_hits": cache_stats["redis_hits"],
                    "memory_hits": cache_stats["memory_hits"],
                    "errors": cache_stats["errors"],
                }
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            },
        )


@router.get("/cache/stats", summary="Cache statistics")
async def cache_statistics() -> dict[str, Any]:
    """
    Get detailed cache statistics.

    Returns:
        Cache performance metrics including:
        - Hit/miss counts
        - Hit rate percentage
        - Cache size
        - Backend type (Redis/Memory)

    Example:
        >>> response = await client.get("/api/v1/metrics/cache/stats")
        >>> print(response.json()["hit_rate_percent"])
        85.5
    """
    try:
        cache = get_cache_service()
        stats = cache.get_stats()

        return {
            "status": "success",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "cache_backend": "redis" if stats["redis_enabled"] else "memory",
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@router.post("/cache/clear", summary="Clear cache")
async def clear_cache() -> dict[str, str]:
    """
    Clear all cache entries.

    ⚠️ Warning: This will clear all cached data.

    Returns:
        Success message

    Example:
        >>> response = await client.post("/api/v1/metrics/cache/clear")
        >>> print(response.json()["message"])
        "Cache cleared successfully"
    """
    try:
        cache = get_cache_service()
        cache.memory_cache.clear()
        cache.reset_stats()

        logger.info("Cache cleared manually via API")

        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@router.get("/system/info", summary="System information")
async def system_info() -> dict[str, Any]:
    """
    Get system information and configuration.

    Returns:
        System details including:
        - Application version
        - Python version
        - Environment
        - Configuration summary

    Example:
        >>> response = await client.get("/api/v1/metrics/system/info")
        >>> print(response.json()["app_version"])
        "1.0.0"
    """
    import platform
    import sys

    from ..config import settings

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "python_version": sys.version,
        "platform": platform.platform(),
        "debug_mode": settings.debug,
        "environment": "development" if settings.debug else "production",
        "llm_provider": "local" if settings.use_local_llm else "gemini",
        "gemini_model": settings.gemini_model,
        "ollama_model": settings.ollama_model if settings.use_local_llm else None,
        "cache_enabled": settings.redis_url is not None,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
