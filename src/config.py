"""
Configuration module for Nur Al-Ilm Islamic Knowledge Assistant.

This module handles all application configuration including API keys,
environment variables, and application settings.
"""

import os
from typing import Optional

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

    # LLM Configuration
    use_local_llm: bool = Field(
        default=False,
        description="Use local LLM (Ollama) instead of Gemini",
    )
    
    # Google Gemini Configuration
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key - SET IN .env FILE",
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
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL for caching",
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


# Global settings instance
settings = Settings()

