"""
Configuration module for Nur Al-Ilm Islamic Knowledge Assistant.

This module handles all application configuration including API keys,
environment variables, and application settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Configuration
    app_name: str = Field(
        default="Al-Muwatta - الموطأ | Maliki Fiqh Assistant",
        description="Application name",
    )
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=True, description="Debug mode")
    app_base_url: str | None = Field(
        default=None, description="Public base URL used for provider headers"
    )

    # LLM Configuration
    use_local_llm: bool = Field(
        default=False,
        description="Use local LLM (Ollama) instead of Gemini",
    )

    # Google Gemini Configuration (Optional - only needed if using Gemini provider)
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini API key (optional - only required when using Gemini provider)",
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini model to use",
    )

    # Ollama Configuration
    ollama_model: str = Field(
        default="qwen2.5:7b",
        description="Ollama model name (for local inference)",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )

    # External API Keys / Toggles
    sunnah_api_key: str | None = Field(
        default=None,
        description="API key for sunnah.com hadith API",
    )
    muslim_salat_api_key: str | None = Field(
        default=None,
        description="Optional API key for MuslimSalat prayer times API",
    )
    quran_com_use_live_api: bool = Field(
        default=True,
        description="Whether to call Quran.com API v4 before falling back to AlQuran Cloud",
    )

    # API Rate Limiting
    rate_limit_calls: int = Field(
        default=100,
        description="Number of API calls allowed",
    )
    rate_limit_period: int = Field(
        default=60,
        description="Rate limit period in seconds",
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./nur_al_ilm.db",
        description="Database connection URL",
    )

    # Redis Configuration
    redis_url: str | None = Field(
        default=None,
        description="Redis connection URL for caching",
    )

    # Qdrant Configuration
    qdrant_url: str | None = Field(
        default=None,
        description="Qdrant server URL (e.g., http://localhost:6333). If not set, uses embedded local DB.",
    )

    # Web Search / Firecrawl
    firecrawl_api_key: str | None = Field(
        default=None,
        description="Firecrawl API key for web scraping (optional)",
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    # API Timeouts
    api_timeout: int = Field(default=30, description="API request timeout in seconds")

    # Cache Settings
    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
    )

    # Security Configuration
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        description="Comma-separated list of allowed CORS origins",
    )


# Global settings instance
settings = Settings()
