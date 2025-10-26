"""
Prayer Times API Client for fetching Islamic prayer times and calendar data.

This client interfaces with:
- aladhan.com API (free, comprehensive Islamic calendar API)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from .base_client import BaseAPIClient


class PrayerTimesAPIClient(BaseAPIClient):
    """Client for accessing prayer times and Islamic calendar data."""

    # API Documentation: https://aladhan.com/prayer-times-api
    ALADHAN_API_BASE = "https://api.aladhan.com/v1"

    def __init__(self) -> None:
        """Initialize the Prayer Times API client."""
        super().__init__(base_url=self.ALADHAN_API_BASE)

    async def get_timings(
        self,
        latitude: float,
        longitude: float,
        method: int = 2,
        date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times for a specific location and date.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            method: Calculation method (default: 2 - Islamic Society of North America)
                1 - University of Islamic Sciences, Karachi
                2 - Islamic Society of North America (ISNA)
                3 - Muslim World League (MWL)
                4 - Umm al-Qura, Makkah
                5 - Egyptian General Authority of Survey
                7 - Institute of Geophysics, University of Tehran
                8 - Gulf Region
                9 - Kuwait
                10 - Qatar
                11 - Majlis Ugama Islam Singapura
                12 - Union Organization islamic de France
                13 - Diyanet İşleri Başkanlığı, Turkey
            date: Date in DD-MM-YYYY format (defaults to today)

        Returns:
            Prayer times data or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> times = await client.get_timings(21.3891, 39.8579)  # Makkah
            >>> print(times['timings']['Fajr'])
            >>> print(times['timings']['Dhuhr'])
        """
        try:
            if date is None:
                date = datetime.now().strftime("%d-%m-%Y")

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method,
            }

            response = await self.get(f"/timings/{date}", params=params)
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get prayer timings: {e}")
            return None

    async def get_timings_by_city(
        self,
        city: str,
        country: str,
        method: int = 2,
        date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times by city and country.

        Args:
            city: City name
            country: Country name or ISO code
            method: Calculation method (see get_timings for options)
            date: Date in DD-MM-YYYY format (defaults to today)

        Returns:
            Prayer times data or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> times = await client.get_timings_by_city('Dubai', 'UAE')
            >>> print(times['timings'])
        """
        try:
            if date is None:
                date = datetime.now().strftime("%d-%m-%Y")

            params = {
                "city": city,
                "country": country,
                "method": method,
            }

            response = await self.get(f"/timingsByCity/{date}", params=params)
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get prayer timings for {city}, {country}: {e}")
            return None

    async def get_timings_by_address(
        self,
        address: str,
        method: int = 2,
        date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times by address (geocoded automatically).

        Args:
            address: Full address string
            method: Calculation method
            date: Date in DD-MM-YYYY format (defaults to today)

        Returns:
            Prayer times data or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> times = await client.get_timings_by_address('Masjid Al Haram, Makkah, Saudi Arabia')
            >>> print(times['timings'])
        """
        try:
            if date is None:
                date = datetime.now().strftime("%d-%m-%Y")

            params = {
                "address": address,
                "method": method,
            }

            response = await self.get(f"/timingsByAddress/{date}", params=params)
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get prayer timings for address '{address}': {e}")
            return None

    async def get_calendar(
        self,
        latitude: float,
        longitude: float,
        month: int,
        year: int,
        method: int = 2,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times calendar for an entire month.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            month: Month number (1-12)
            year: Year
            method: Calculation method

        Returns:
            Monthly prayer times calendar or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> calendar = await client.get_calendar(21.3891, 39.8579, 10, 2025)
            >>> for day in calendar:
            ...     print(day['date']['readable'], day['timings']['Fajr'])
        """
        try:
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12")

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method,
                "month": month,
                "year": year,
            }

            response = await self.get(f"/calendar/{year}/{month}", params=params)
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid month value: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get calendar for {month}/{year}: {e}")
            return None

    async def get_calendar_by_city(
        self,
        city: str,
        country: str,
        month: int,
        year: int,
        method: int = 2,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times calendar for a city for an entire month.

        Args:
            city: City name
            country: Country name or ISO code
            month: Month number (1-12)
            year: Year
            method: Calculation method

        Returns:
            Monthly prayer times calendar or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> calendar = await client.get_calendar_by_city('Cairo', 'Egypt', 10, 2025)
            >>> for day in calendar:
            ...     print(day['date']['hijri']['date'])
        """
        try:
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12")

            params = {
                "city": city,
                "country": country,
                "method": method,
            }

            response = await self.get(f"/calendarByCity/{year}/{month}", params=params)
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid month value: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get calendar for {city}, {country}: {e}")
            return None

    async def get_hijri_calendar(
        self,
        latitude: float,
        longitude: float,
        month: int,
        year: int,
        method: int = 2,
    ) -> Optional[Dict[str, Any]]:
        """
        Get prayer times calendar using Hijri dates.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            month: Hijri month number (1-12)
            year: Hijri year
            method: Calculation method

        Returns:
            Monthly prayer times calendar in Hijri or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> calendar = await client.get_hijri_calendar(21.3891, 39.8579, 9, 1447)  # Ramadan 1447
            >>> for day in calendar:
            ...     print(day['date']['hijri']['day'])
        """
        try:
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12")

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method,
            }

            response = await self.get(
                f"/hijriCalendar/{year}/{month}",
                params=params,
            )
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid month value: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get Hijri calendar for {month}/{year}: {e}")
            return None

    async def get_current_date(self) -> Optional[Dict[str, Any]]:
        """
        Get current Gregorian and Hijri dates.

        Returns:
            Current date information or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> date_info = await client.get_current_date()
            >>> print(date_info['hijri']['month']['ar'])
            >>> print(date_info['gregorian']['month']['en'])
        """
        try:
            response = await self.get("/currentDate")
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get current date: {e}")
            return None

    async def get_hijri_date_from_gregorian(
        self,
        day: int,
        month: int,
        year: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Convert Gregorian date to Hijri.

        Args:
            day: Day (1-31)
            month: Month (1-12)
            year: Year

        Returns:
            Hijri date information or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> hijri = await client.get_hijri_date_from_gregorian(26, 10, 2025)
            >>> print(hijri['hijri']['date'])
        """
        try:
            response = await self.get(f"/gToH/{day}-{month}-{year}")
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to convert {day}-{month}-{year} to Hijri: {e}")
            return None

    async def get_gregorian_date_from_hijri(
        self,
        day: int,
        month: int,
        year: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Convert Hijri date to Gregorian.

        Args:
            day: Day (1-30)
            month: Hijri month (1-12)
            year: Hijri year

        Returns:
            Gregorian date information or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> gregorian = await client.get_gregorian_date_from_hijri(3, 4, 1447)
            >>> print(gregorian['gregorian']['date'])
        """
        try:
            response = await self.get(f"/hToG/{day}-{month}-{year}")
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to convert Hijri {day}-{month}-{year} to Gregorian: {e}")
            return None

    async def get_qibla_direction(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Get Qibla direction for a specific location.

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Qibla direction in degrees or None if request fails

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> qibla = await client.get_qibla_direction(40.7128, -74.0060)  # New York
            >>> print(f"Qibla direction: {qibla['direction']}°")
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
            }

            response = await self.get("/qibla", params=params)
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get Qibla direction: {e}")
            return None

    async def get_asma_al_husna(self) -> List[Dict[str, Any]]:
        """
        Get the 99 Names of Allah (Asma Al-Husna).

        Returns:
            List of Allah's names with translations and transliterations

        Example:
            >>> client = PrayerTimesAPIClient()
            >>> names = await client.get_asma_al_husna()
            >>> for name in names[:5]:
            ...     print(name['name'], name['en']['meaning'])
        """
        try:
            response = await self.get("/asmaAlHusna")
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Asma Al-Husna: {e}")
            return []

