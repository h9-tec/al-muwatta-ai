"""
Ollama Service for Local LLM Inference.

This service provides an alternative to Google Gemini using locally-run LLMs.
"""

from loguru import logger

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not installed. Run: pip install ollama")


class OllamaService:
    """Service for local LLM inference using Ollama."""

    def __init__(self, model: str = "qwen2.5:7b") -> None:
        """
        Initialize Ollama service.

        Args:
            model: Ollama model name (default: qwen2.5:7b for Arabic)
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama is not installed. Run: pip install ollama")

        self.model = model
        self.client = ollama.Client()

        try:
            # Test if model exists
            self.client.show(model)
            logger.info(f"✅ Ollama service initialized with model: {model}")
        except Exception as e:
            logger.warning(f"Model {model} not found. Pull it with: ollama pull {model}")
            logger.error(f"Ollama initialization error: {e}")

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str | None:
        """
        Generate content using local Ollama model.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text or None if failed

        Example:
            >>> service = OllamaService()
            >>> response = await service.generate_content("What is Tawheed?")
            >>> print(response)
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            content = response.get("response", "")
            if content:
                logger.info("✅ Content generated with Ollama")
                return content

            logger.warning("No content generated")
            return None

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None

    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
    ) -> str | None:
        """
        Chat interface with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature

        Returns:
            Generated response

        Example:
            >>> messages = [
            ...     {"role": "user", "content": "What are the pillars of Islam?"}
            ... ]
            >>> response = await service.chat(messages)
        """
        try:
            response = self.client.chat(
                model=self.model, messages=messages, options={"temperature": temperature}
            )

            return response.get("message", {}).get("content")

        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            return None

    def list_models(self) -> list:
        """
        List available Ollama models.

        Returns:
            List of model names
        """
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model from Ollama registry.

        Args:
            model_name: Model to download (e.g., 'qwen2.5:7b')

        Returns:
            True if successful
        """
        try:
            logger.info(f"Pulling model: {model_name}")
            self.client.pull(model_name)
            logger.info(f"✅ Model {model_name} downloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False
