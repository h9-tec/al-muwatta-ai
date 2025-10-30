"""
Comprehensive tests for Prayer Times API Client.

This module tests all functionality of the PrayerTimesAPIClient including
prayer times retrieval, calendar access, date conversions, and Islamic features.
"""

import pytest

from src.api_clients import PrayerTimesAPIClient


class TestPrayerTimesAPIClient:
    """Test suite for PrayerTimesAPIClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the Prayer Times client initializes correctly."""
        client = PrayerTimesAPIClient()
        assert client is not None
        assert client.base_url == PrayerTimesAPIClient.ALADHAN_API_BASE
        await client.close()

    @pytest.mark.asyncio
    async def test_get_timings_by_coordinates(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting prayer times by coordinates (Makkah)."""
        latitude = 21.3891
        longitude = 39.8579

        timings = await prayer_times_client.get_timings(latitude, longitude)

        assert timings is not None
        assert isinstance(timings, dict)
        assert "timings" in timings

        # Verify all five daily prayers are present
        prayer_timings = timings["timings"]
        assert "Fajr" in prayer_timings
        assert "Dhuhr" in prayer_timings
        assert "Asr" in prayer_timings
        assert "Maghrib" in prayer_timings
        assert "Isha" in prayer_timings

    @pytest.mark.asyncio
    async def test_get_timings_with_specific_date(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting prayer times for a specific date."""
        latitude = 21.3891
        longitude = 39.8579
        date = "01-01-2025"

        timings = await prayer_times_client.get_timings(
            latitude,
            longitude,
            date=date,
        )

        assert timings is not None
        assert isinstance(timings, dict)
        assert "date" in timings

    @pytest.mark.asyncio
    async def test_get_timings_by_city(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting prayer times by city name."""
        city = "Dubai"
        country = "UAE"

        timings = await prayer_times_client.get_timings_by_city(city, country)

        assert timings is not None
        assert isinstance(timings, dict)
        assert "timings" in timings

        prayer_timings = timings["timings"]
        assert "Fajr" in prayer_timings

    @pytest.mark.asyncio
    async def test_get_timings_by_address(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting prayer times by address."""
        address = "Masjid Al Haram, Makkah, Saudi Arabia"

        timings = await prayer_times_client.get_timings_by_address(address)

        assert timings is not None
        assert isinstance(timings, dict)
        assert "timings" in timings

    @pytest.mark.asyncio
    async def test_get_calendar(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting monthly prayer times calendar."""
        latitude = 21.3891
        longitude = 39.8579
        month = 10
        year = 2025

        calendar = await prayer_times_client.get_calendar(
            latitude,
            longitude,
            month,
            year,
        )

        assert calendar is not None
        assert isinstance(calendar, list)

        # Calendar should have ~30 days
        assert len(calendar) >= 28
        assert len(calendar) <= 31

        # Each day should have timings
        first_day = calendar[0]
        assert "timings" in first_day
        assert "date" in first_day

    @pytest.mark.asyncio
    async def test_get_calendar_invalid_month(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting calendar with invalid month."""
        latitude = 21.3891
        longitude = 39.8579
        month = 13  # Invalid
        year = 2025

        calendar = await prayer_times_client.get_calendar(
            latitude,
            longitude,
            month,
            year,
        )

        assert calendar is None

    @pytest.mark.asyncio
    async def test_get_calendar_by_city(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting calendar by city."""
        city = "Cairo"
        country = "Egypt"
        month = 10
        year = 2025

        calendar = await prayer_times_client.get_calendar_by_city(
            city,
            country,
            month,
            year,
        )

        assert calendar is not None
        assert isinstance(calendar, list)
        assert len(calendar) >= 28

    @pytest.mark.asyncio
    async def test_get_hijri_calendar(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting Hijri calendar."""
        latitude = 21.3891
        longitude = 39.8579
        month = 9  # Ramadan
        year = 1447

        calendar = await prayer_times_client.get_hijri_calendar(
            latitude,
            longitude,
            month,
            year,
        )

        assert calendar is not None
        assert isinstance(calendar, list)

        if calendar:
            first_day = calendar[0]
            assert "date" in first_day
            assert "hijri" in first_day["date"]

    @pytest.mark.asyncio
    async def test_get_current_date(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting current date in Gregorian and Hijri."""
        date_info = await prayer_times_client.get_current_date()

        assert date_info is not None
        assert isinstance(date_info, dict)
        assert "hijri" in date_info
        assert "gregorian" in date_info

        hijri = date_info["hijri"]
        assert "month" in hijri
        assert "year" in hijri

        gregorian = date_info["gregorian"]
        assert "month" in gregorian
        assert "year" in gregorian

    @pytest.mark.asyncio
    async def test_gregorian_to_hijri_conversion(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test converting Gregorian date to Hijri."""
        day = 26
        month = 10
        year = 2025

        result = await prayer_times_client.get_hijri_date_from_gregorian(
            day,
            month,
            year,
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "hijri" in result
        assert "gregorian" in result

        hijri = result["hijri"]
        assert "date" in hijri

    @pytest.mark.asyncio
    async def test_hijri_to_gregorian_conversion(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test converting Hijri date to Gregorian."""
        day = 1
        month = 1  # Muharram
        year = 1447

        result = await prayer_times_client.get_gregorian_date_from_hijri(
            day,
            month,
            year,
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "gregorian" in result
        assert "hijri" in result

    @pytest.mark.asyncio
    async def test_get_qibla_direction(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting Qibla direction for New York."""
        latitude = 40.7128
        longitude = -74.0060

        qibla = await prayer_times_client.get_qibla_direction(latitude, longitude)

        assert qibla is not None
        assert isinstance(qibla, dict)
        assert "direction" in qibla

        # Qibla direction should be a number between 0 and 360
        direction = float(qibla["direction"])
        assert 0 <= direction < 360

    @pytest.mark.asyncio
    async def test_get_asma_al_husna(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test getting the 99 Names of Allah."""
        names = await prayer_times_client.get_asma_al_husna()

        assert isinstance(names, list)
        assert len(names) == 99

        # Check structure of first name
        first_name = names[0]
        assert "name" in first_name
        assert "en" in first_name
        assert "meaning" in first_name["en"]

    @pytest.mark.asyncio
    async def test_different_calculation_methods(
        self,
        prayer_times_client: PrayerTimesAPIClient,
    ):
        """Test different prayer time calculation methods."""
        latitude = 21.3891
        longitude = 39.8579

        # Test ISNA method
        timings_isna = await prayer_times_client.get_timings(
            latitude,
            longitude,
            method=2,
        )

        # Test MWL method
        timings_mwl = await prayer_times_client.get_timings(
            latitude,
            longitude,
            method=3,
        )

        assert timings_isna is not None
        assert timings_mwl is not None

        # Different methods may produce different times
        assert isinstance(timings_isna["timings"], dict)
        assert isinstance(timings_mwl["timings"], dict)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using the client as an async context manager."""
        async with PrayerTimesAPIClient() as client:
            assert client is not None
            timings = await client.get_timings(21.3891, 39.8579)
            assert timings is not None
