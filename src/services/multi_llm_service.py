"""
Multi-Provider LLM Service.

Supports: Ollama, OpenRouter, Groq, OpenAI, Claude, and Gemini.
Automatically fetches available models from each provider.
"""

from typing import Optional, Dict, Any, List
from loguru import logger
import httpx
import os

from ..config import settings


def _safe_ascii(value: Optional[str], fallback: str) -> str:
    if not value:
        return fallback
    try:
        value.encode("ascii")
        return value
    except UnicodeEncodeError:
        cleaned = value.encode("ascii", "ignore").decode() or fallback
        return cleaned


def validate_api_key(provider: str, api_key: Optional[str]) -> Optional[str]:
    """
    Validate API key format and basic security checks.
    
    Args:
        provider: Provider name
        api_key: API key to validate
    
    Returns:
        Sanitized API key if valid, None otherwise
    """
    if not api_key:
        return None
    
    sanitized_key = api_key.strip()
    
    # Basic length check (most API keys are at least 10 chars)
    if len(sanitized_key) < 10:
        logger.warning(f"API key too short for provider {provider}")
        return None
    
    # Check for common invalid patterns
    invalid_patterns = [
        "your_api_key",
        "api_key_here",
        "test_key",
        "example",
    ]
    
    api_key_lower = sanitized_key.lower()
    for pattern in invalid_patterns:
        if pattern in api_key_lower:
            logger.warning(f"API key contains suspicious pattern: {pattern}")
            return None
    
    # Return sanitized key
    return sanitized_key


class MultiLLMService:
    """Unified service supporting multiple LLM providers."""

    PROVIDERS = {
        "ollama": {
            "name": "Ollama (Local)",
            "base_url": "http://localhost:11434",
            "requires_api_key": False,
        },
        "openrouter": {
            "name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1",
            "requires_api_key": True,
        },
        "groq": {
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "requires_api_key": True,
        },
        "openai": {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "requires_api_key": True,
        },
        "anthropic": {
            "name": "Claude (Anthropic)",
            "base_url": "https://api.anthropic.com/v1",
            "requires_api_key": True,
        },
        "gemini": {
            "name": "Google Gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "requires_api_key": True,
        },
    }

    def __init__(self, provider: str = "ollama", api_key: Optional[str] = None):
        """
        Initialize multi-provider LLM service.

        Args:
            provider: Provider name ('ollama', 'openrouter', 'groq', etc.)
            api_key: API key for the provider (if required)
        
        Raises:
            ValueError: If provider is unknown or API key is invalid
        """
        self.provider = provider.lower()
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.provider_info = self.PROVIDERS[self.provider]
        self.base_url = self.provider_info["base_url"]
        
        # Validate and sanitize API key if required
        if self.provider_info["requires_api_key"]:
            if not api_key:
                raise ValueError(f"{self.provider} requires an API key")
            
            # Validate API key format
            validated_key = validate_api_key(self.provider, api_key)
            if not validated_key:
                raise ValueError(f"Invalid API key format for {self.provider}")
            
            self.api_key = validated_key
        else:
            self.api_key = None
        
        logger.info(f"✅ Initialized {self.provider_info['name']}")

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Fetch all available models from the provider.

        Returns:
            List of model dictionaries with name, size, description
        """
        try:
            if self.provider == "ollama":
                return await self._list_ollama_models()
            elif self.provider == "openrouter":
                return await self._list_openrouter_models()
            elif self.provider == "groq":
                return await self._list_groq_models()
            elif self.provider == "openai":
                return await self._list_openai_models()
            elif self.provider == "anthropic":
                return await self._list_anthropic_models()
            elif self.provider == "gemini":
                return await self._list_gemini_models()
            
            return []

        except Exception as e:
            logger.error(f"Failed to list models from {self.provider}: {e}")
            return []

    async def _list_ollama_models(self) -> List[Dict[str, Any]]:
        """List locally installed Ollama models."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                response = await client.get("/api/tags")
                response.raise_for_status()
                data = response.json()

            models: List[Dict[str, Any]] = []
            for model in data.get("models", []):
                name = model.get("name") or model.get("model")
                if not name:
                    continue
                models.append(
                    {
                        "id": name,
                        "name": name,
                        "provider": "ollama",
                        "size": model.get("size"),
                        "modified_at": model.get("modified_at"),
                        "local": True,
                    }
                )

            return models

        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    async def _list_openrouter_models(self) -> List[Dict[str, Any]]:
        """Fetch OpenRouter available models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model in data.get('data', []):
                    # Filter for good Arabic-friendly models
                    model_id = model.get('id')
                    if not model_id:
                        continue

                    if any(x in model_id.lower() for x in ['qwen', 'llama', 'mistral', 'gemini']):
                        safe_name = _safe_ascii(model.get('name', model_id), model_id)
                        models.append({
                            'id': model_id,
                            'name': safe_name,
                            'context_length': model.get('context_length', 0),
                            'provider': 'openrouter',
                            'pricing': model.get('pricing', {}),
                        })
                
                return models

        except Exception as e:
            logger.error(f"Failed to list OpenRouter models: {e}")
            return []

    async def _list_groq_models(self) -> List[Dict[str, Any]]:
        """Fetch Groq available models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                
                data = response.json()
                return [
                    {
                        'id': model['id'],
                        'name': model['id'],
                        'provider': 'groq',
                        'context_length': model.get('context_window', 0),
                    }
                    for model in data.get('data', [])
                ]

        except Exception as e:
            logger.error(f"Failed to list Groq models: {e}")
            return []

    async def _list_openai_models(self) -> List[Dict[str, Any]]:
        """Fetch OpenAI available models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                
                data = response.json()
                # Filter for GPT models
                return [
                    {
                        'id': model['id'],
                        'name': model['id'],
                        'provider': 'openai',
                    }
                    for model in data.get('data', [])
                    if 'gpt' in model['id'].lower()
                ]

        except Exception as e:
            logger.error(f"Failed to list OpenAI models: {e}")
            return []

    async def _list_anthropic_models(self) -> List[Dict[str, Any]]:
        """List Claude models."""
        # Anthropic doesn't have a models endpoint, return known models
        return [
            {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'provider': 'anthropic'},
            {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus', 'provider': 'anthropic'},
            {'id': 'claude-3-sonnet-20240229', 'name': 'Claude 3 Sonnet', 'provider': 'anthropic'},
            {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku', 'provider': 'anthropic'},
        ]

    async def _list_gemini_models(self) -> List[Dict[str, Any]]:
        """List Gemini models."""
        return [
            {'id': 'gemini-2.0-flash-exp', 'name': 'Gemini 2.0 Flash', 'provider': 'gemini'},
            {'id': 'gemini-exp-1206', 'name': 'Gemini Experimental', 'provider': 'gemini'},
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'provider': 'gemini'},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'provider': 'gemini'},
        ]

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Optional[str]:
        """
        Generate text using the selected provider and model.

        Args:
            prompt: Input prompt
            model: Model ID to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            if self.provider == "ollama":
                return await self._generate_ollama(prompt, model, temperature, max_tokens)
            else:
                # OpenAI-compatible API (OpenRouter, Groq, OpenAI)
                return await self._generate_openai_compatible(prompt, model, temperature, max_tokens)

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None

    async def _generate_ollama(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Optional[str]:
        """Generate using Ollama."""
        try:
            import ollama
            client = ollama.Client()
            
            response = client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                }
            )
            
            return response.get('response', '')

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None

    async def _generate_openai_compatible(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Optional[str]:
        """Generate using OpenAI-compatible APIs."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            if self.provider == "openrouter":
                headers.setdefault(
                    "HTTP-Referer",
                    _safe_ascii(settings.app_base_url, "http://localhost"),
                )
                headers.setdefault(
                    "X-Title",
                    _safe_ascii(settings.app_name, "Al-Muwatta"),
                )

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                response.raise_for_status()

                data = response.json()
                return data['choices'][0]['message']['content']

        except httpx.HTTPStatusError as exc:
            logger.error(
                f"API generation failed ({self.provider}) - status {exc.response.status_code}: {exc.response.text}"
            )
            return None
        except Exception as e:
            logger.error(f"API generation failed ({self.provider}): {e}")
            return None

