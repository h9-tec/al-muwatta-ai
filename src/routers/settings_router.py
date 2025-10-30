"""
Settings Router for LLM Provider Configuration.

Allows users to select provider, input API keys, and choose models.
Also includes cache management and statistics.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from loguru import logger

from ..services.multi_llm_service import MultiLLMService
from ..services.cache_service import get_cache_service
from ..config import settings

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


class ProviderConfig(BaseModel):
    """Provider configuration model."""
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None


class ProviderModelsRequest(BaseModel):
    api_key: Optional[str] = None


@router.get("/providers", summary="Get all available providers")
async def get_providers() -> Dict[str, Any]:
    """
    Get list of all supported LLM providers.

    Returns:
        Dictionary of providers with their details
    """
    providers = MultiLLMService.PROVIDERS.copy()
    if settings.use_local_llm:
        providers.setdefault("ollama", {"name": "Ollama (Local)", "requires_api_key": False})

    return {
        "providers": providers,
        "current": "gemini",  # Default
    }


@router.post("/providers/{provider}/models", summary="List models for provider")
async def list_provider_models(
    provider: str,
    payload: Optional[ProviderModelsRequest] = Body(default=None, description="Optional API key payload"),
) -> Dict[str, Any]:
    """
    Fetch all available models from a provider.

    Args:
        provider: Provider name (ollama, openrouter, groq, etc.)
        payload: Optional body containing `api_key` when the provider requires it

    Returns:
        List of available models
    """
    try:
        # Use API key only if provided via payload
        provided_key = payload.api_key if (payload and payload.api_key) else None
        service = MultiLLMService(provider=provider, api_key=provided_key)
        models = await service.list_available_models()
        
        return {
            "provider": provider,
            "models_count": len(models),
            "models": models,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection", summary="Test provider connection")
async def test_provider_connection(
    provider: str = Body(..., description="Provider name"),
    api_key: str = Body(None, description="API key"),
    model: str = Body(None, description="Model to test"),
) -> Dict[str, Any]:
    """
    Test connection to a provider and generate sample text.

    Args:
        provider: Provider name
        api_key: API key
        model: Model ID to test

    Returns:
        Test result with sample generation
    """
    try:
        service = MultiLLMService(provider=provider, api_key=api_key)
        
        # Get models if not specified
        if not model:
            models = await service.list_available_models()
            if not models:
                raise HTTPException(
                    status_code=404,
                    detail="No models available"
                )
            model = models[0]['id']
        
        # Test generation
        test_prompt = "Say 'Connection successful' in one sentence."
        response = await service.generate(
            prompt=test_prompt,
            model=model,
            temperature=0.5,
            max_tokens=50,
        )
        
        if response:
            return {
                "status": "success",
                "provider": provider,
                "model": model,
                "test_response": response,
                "message": "✅ Connection successful!"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No response from model"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Connection failed: {str(e)}"
        )


@router.get("/ollama/status", summary="Check Ollama server status")
async def check_ollama_status() -> Dict[str, Any]:
    """
    Check if Ollama server is running and list installed models.

    Returns:
        Ollama status and installed models
    """
    try:
        import ollama
        client = ollama.Client()
        
        # Try to list models
        models_response = client.list()
        models = models_response.get('models', [])
        
        return {
            "status": "running",
            "models_installed": len(models),
            "models": [
                {
                    'name': m['name'],
                    'size': m.get('size', 0),
                    'modified': m.get('modified_at', ''),
                }
                for m in models
            ],
            "message": "✅ Ollama is running"
        }

    except Exception as e:
        return {
            "status": "not_running",
            "models_installed": 0,
            "models": [],
            "message": "❌ Ollama not running. Start with: ollama serve",
            "error": str(e),
        }


@router.post("/ollama/pull-model", summary="Download Ollama model")
async def pull_ollama_model(
    model_name: str = Body(..., description="Model to download (e.g., qwen2.5:7b)"),
) -> Dict[str, Any]:
    """
    Download a model from Ollama registry.

    Args:
        model_name: Model name to download

    Returns:
        Download status
    """
    try:
        import ollama
        client = ollama.Client()
        
        logger.info(f"Pulling Ollama model: {model_name}")
        
        # This will stream the download
        client.pull(model_name)
        
        return {
            "status": "success",
            "model": model_name,
            "message": f"✅ Model {model_name} downloaded successfully"
        }

    except Exception as e:
        logger.error(f"Failed to pull model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/cache/stats", summary="Get cache statistics")
async def get_cache_statistics() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics.
    
    Returns:
        Cache performance metrics including:
        - Hit/miss rates
        - Redis vs in-memory distribution
        - Total requests served
        - Error count
        - Current cache sizes
    """
    try:
        cache = get_cache_service()
        stats = cache.get_stats()
        
        return {
            "status": "success",
            "statistics": stats,
            "message": f"Cache hit rate: {stats['hit_rate_percent']}%"
        }
    
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@router.post("/cache/clear/{pattern}", summary="Clear cache by pattern")
async def clear_cache_pattern(pattern: str) -> Dict[str, Any]:
    """
    Clear all cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match (e.g., "prayer_times:*", "quran_*")
    
    Returns:
        Number of keys cleared
    
    Examples:
        - Clear all prayer times: /cache/clear/prayer_times:*
        - Clear all Quran data: /cache/clear/quran_*
        - Clear all cache: /cache/clear/*
    """
    try:
        cache = get_cache_service()
        deleted_count = await cache.clear_pattern(pattern)
        
        return {
            "status": "success",
            "pattern": pattern,
            "keys_deleted": deleted_count,
            "message": f"✅ Cleared {deleted_count} cache entries matching '{pattern}'"
        }
    
    except Exception as e:
        logger.error(f"Failed to clear cache pattern '{pattern}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.post("/cache/reset-stats", summary="Reset cache statistics")
async def reset_cache_statistics() -> Dict[str, Any]:
    """
    Reset all cache statistics counters to zero.
    
    Returns:
        Success message
    """
    try:
        cache = get_cache_service()
        cache.reset_stats()
        
        return {
            "status": "success",
            "message": "✅ Cache statistics reset successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to reset cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset cache statistics: {str(e)}"
        )

