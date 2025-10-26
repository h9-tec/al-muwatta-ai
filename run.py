#!/usr/bin/env python3
"""
Nur Al-Ilm - Quick Start Script

This script starts the FastAPI server for the Islamic Knowledge Assistant.
"""

import uvicorn
from src.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Using Gemini model: {settings.gemini_model}")
    print("\n🌟 Server will be available at:")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📚 Alternative Docs: http://localhost:8000/redoc")
    print("\n✨ Press CTRL+C to stop the server\n")

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

