"""
Settings Router for LLM Provider Configuration.

Allows users to select provider, input API keys, and choose models.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from loguru import logger

from ..services.multi_llm_service import MultiLLMService

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


class ProviderConfig(BaseModel):
    """Provider configuration model."""
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None


@router.get("/providers", summary="Get all available providers")
async def get_providers() -> Dict[str, Any]:
    """
    Get list of all supported LLM providers.

    Returns:
        Dictionary of providers with their details
    """
    return {
        "providers": MultiLLMService.PROVIDERS,
        "current": "gemini",  # Default
    }


@router.post("/providers/{provider}/models", summary="List models for provider")
async def list_provider_models(
    provider: str,
    api_key: str = Body(None, description="API key (if required)"),
) -> Dict[str, Any]:
    """
    Fetch all available models from a provider.

    Args:
        provider: Provider name (ollama, openrouter, groq, etc.)
        api_key: API key for the provider

    Returns:
        List of available models
    """
    try:
        service = MultiLLMService(provider=provider, api_key=api_key)
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

