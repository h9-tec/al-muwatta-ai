"""API routers for different endpoints."""

from .ai_router import router as ai_router
from .hadith_router import router as hadith_router
from .prayer_times_router import router as prayer_times_router
from .quran_router import router as quran_router
from .settings_router import router as settings_router
from .upload_router import router as upload_router

__all__ = [
    "hadith_router",
    "quran_router",
    "prayer_times_router",
    "ai_router",
    "upload_router",
    "settings_router",
]
