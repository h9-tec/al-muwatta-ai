"""
Unified Local LLM Service supporting both Ollama and llama.cpp.

This service allows switching between cloud (Gemini) and local (Ollama/llama.cpp) LLMs.
"""

from typing import Optional
from loguru import logger

from ..config import settings


class LocalLLMService:
    """
    Unified service for local LLM inference.
    
    Supports:
    - Ollama (preferred - easy to use)
    - llama.cpp (for advanced users)
    """

    def __init__(
        self,
        backend: str = "ollama",
        model: str = "qwen2.5:7b",
    ) -> None:
        """
        Initialize local LLM service.

        Args:
            backend: 'ollama' or 'llamacpp'
            model: Model name/path
        """
        self.backend = backend
        self.model_name = model
        self.service = None

        if backend == "ollama":
            self._init_ollama(model)
        elif backend == "llamacpp":
            self._init_llamacpp(model)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def _init_ollama(self, model: str) -> None:
        """Initialize Ollama backend."""
        try:
            from .ollama_service import OllamaService
            self.service = OllamaService(model=model)
            logger.info(f"✅ Using Ollama with model: {model}")
        except ImportError:
            logger.error("Ollama not installed. Run: pip install ollama")
            raise

    def _init_llamacpp(self, model_path: str) -> None:
        """Initialize llama.cpp backend."""
        try:
            from llama_cpp import Llama
            
            self.service = Llama(
                model_path=model_path,
                n_ctx=4096,  # Context window
                n_threads=8,  # CPU threads
                n_gpu_layers=0,  # Set to -1 for full GPU offload
            )
            logger.info(f"✅ Using llama.cpp with model: {model_path}")
        except ImportError:
            logger.error("llama-cpp-python not installed. Run: pip install llama-cpp-python")
            raise

    async def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using the configured backend.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if self.backend == "ollama":
            return await self.service.generate_content(prompt, temperature=temperature)
        elif self.backend == "llamacpp":
            output = self.service(
                prompt,
                max_tokens=1000,
                temperature=temperature,
                stop=["Human:", "User:"],
            )
            return output['choices'][0]['text']
        
        return None


# Helper function to auto-select best available LLM
def get_best_available_llm():
    """
    Auto-select best available LLM (Gemini > Ollama > llama.cpp).

    Returns:
        Initialized LLM service
    """
    # Try Gemini first
    if settings.gemini_api_key and settings.gemini_api_key != "your_key_here":
        from .gemini_service import GeminiService
        logger.info("Using Google Gemini (cloud)")
        return GeminiService()
    
    # Try Ollama
    try:
        from .ollama_service import OllamaService
        logger.info("Using Ollama (local)")
        return OllamaService()
    except:
        pass
    
    # Fallback to error
    raise RuntimeError("No LLM available. Install Ollama or set GEMINI_API_KEY")

