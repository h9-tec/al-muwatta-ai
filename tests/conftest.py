"""
Pytest configuration and fixtures for testing.

This module provides common fixtures and configuration for all tests.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from src.api_clients import (
    HadithAPIClient,
    PrayerTimesAPIClient,
    QuranAPIClient,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def hadith_client() -> AsyncGenerator[HadithAPIClient, None]:
    """Provide a Hadith API client for testing."""
    client = HadithAPIClient()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def quran_client() -> AsyncGenerator[QuranAPIClient, None]:
    """Provide a Quran API client for testing."""
    client = QuranAPIClient()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def prayer_times_client() -> AsyncGenerator[PrayerTimesAPIClient, None]:
    """Provide a Prayer Times API client for testing."""
    client = PrayerTimesAPIClient()
    yield client
    await client.close()
