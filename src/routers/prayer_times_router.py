"""
Prayer Times API Router.

This router provides endpoints for prayer times, Islamic calendar, and related features.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ..api_clients import PrayerTimesAPIClient

router = APIRouter(prefix="/api/v1/prayer-times", tags=["Prayer Times"])


@router.get("/timings", summary="Get prayer times by coordinates")
async def get_prayer_timings(
    latitude: float = Query(..., description="Location latitude", ge=-90, le=90),
    longitude: float = Query(..., description="Location longitude", ge=-180, le=180),
    method: int = Query(2, description="Calculation method", ge=1, le=13),
    date: str = Query(None, description="Date in DD-MM-YYYY format"),
) -> dict[str, Any]:
    """
    Get prayer times for a specific location and date.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        method: Calculation method (default: 2 - ISNA)
        date: Optional date (defaults to today)

    Returns:
        Prayer times data
    """
    async with PrayerTimesAPIClient() as client:
        timings = await client.get_timings(latitude, longitude, method=method, date=date)

        if not timings:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch prayer times",
            )

        return {
            "timings": timings,
            "source": "aladhan.com API",
        }


@router.get("/timings/city", summary="Get prayer times by city")
async def get_prayer_timings_by_city(
    city: str = Query(..., description="City name"),
    country: str = Query(..., description="Country name or ISO code"),
    method: int = Query(2, description="Calculation method"),
    date: str = Query(None, description="Date in DD-MM-YYYY format"),
) -> dict[str, Any]:
    """
    Get prayer times by city and country.

    Args:
        city: City name
        country: Country name or ISO code
        method: Calculation method
        date: Optional date

    Returns:
        Prayer times data
    """
    async with PrayerTimesAPIClient() as client:
        timings = await client.get_timings_by_city(
            city,
            country,
            method=method,
            date=date,
        )

        if not timings:
            raise HTTPException(
                status_code=404,
                detail=f"Prayer times not found for {city}, {country}",
            )

        return {
            "timings": timings,
            "location": {"city": city, "country": country},
            "source": "aladhan.com API",
        }


@router.get("/timings/address", summary="Get prayer times by address")
async def get_prayer_timings_by_address(
    address: str = Query(..., description="Full address"),
    method: int = Query(2, description="Calculation method"),
    date: str = Query(None, description="Date in DD-MM-YYYY format"),
) -> dict[str, Any]:
    """
    Get prayer times by address (automatically geocoded).

    Args:
        address: Full address string
        method: Calculation method
        date: Optional date

    Returns:
        Prayer times data
    """
    async with PrayerTimesAPIClient() as client:
        timings = await client.get_timings_by_address(address, method=method, date=date)

        if not timings:
            raise HTTPException(
                status_code=404,
                detail=f"Prayer times not found for address: {address}",
            )

        return {
            "timings": timings,
            "address": address,
            "source": "aladhan.com API",
        }


@router.get("/calendar", summary="Get monthly prayer times calendar")
async def get_prayer_calendar(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    month: int = Query(..., description="Month (1-12)", ge=1, le=12),
    year: int = Query(..., description="Year"),
    method: int = Query(2, description="Calculation method"),
) -> dict[str, Any]:
    """
    Get prayer times calendar for an entire month.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        month: Month number
        year: Year
        method: Calculation method

    Returns:
        Monthly prayer times calendar
    """
    async with PrayerTimesAPIClient() as client:
        calendar = await client.get_calendar(
            latitude,
            longitude,
            month,
            year,
            method=method,
        )

        if not calendar:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch prayer calendar",
            )

        return {
            "calendar": calendar,
            "month": month,
            "year": year,
            "source": "aladhan.com API",
        }


@router.get("/calendar/city", summary="Get monthly calendar by city")
async def get_prayer_calendar_by_city(
    city: str = Query(..., description="City name"),
    country: str = Query(..., description="Country name or ISO code"),
    month: int = Query(..., description="Month (1-12)", ge=1, le=12),
    year: int = Query(..., description="Year"),
    method: int = Query(2, description="Calculation method"),
) -> dict[str, Any]:
    """
    Get prayer times calendar for a city.

    Args:
        city: City name
        country: Country name
        month: Month number
        year: Year
        method: Calculation method

    Returns:
        Monthly prayer times calendar
    """
    async with PrayerTimesAPIClient() as client:
        calendar = await client.get_calendar_by_city(
            city,
            country,
            month,
            year,
            method=method,
        )

        if not calendar:
            raise HTTPException(
                status_code=404,
                detail=f"Calendar not found for {city}, {country}",
            )

        return {
            "calendar": calendar,
            "location": {"city": city, "country": country},
            "month": month,
            "year": year,
            "source": "aladhan.com API",
        }


@router.get("/date/current", summary="Get current date")
async def get_current_date() -> dict[str, Any]:
    """
    Get current Gregorian and Hijri dates.

    Returns:
        Current date information in both calendars
    """
    async with PrayerTimesAPIClient() as client:
        date_info = await client.get_current_date()

        if not date_info:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch current date",
            )

        return {
            "date": date_info,
            "source": "aladhan.com API",
        }


@router.get("/date/convert/gregorian-to-hijri", summary="Convert Gregorian to Hijri")
async def convert_gregorian_to_hijri(
    day: int = Query(..., description="Day", ge=1, le=31),
    month: int = Query(..., description="Month", ge=1, le=12),
    year: int = Query(..., description="Year"),
) -> dict[str, Any]:
    """
    Convert a Gregorian date to Hijri.

    Args:
        day: Day of month
        month: Month
        year: Year

    Returns:
        Hijri date information
    """
    async with PrayerTimesAPIClient() as client:
        result = await client.get_hijri_date_from_gregorian(day, month, year)

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Invalid date",
            )

        return {
            "conversion": result,
            "input": {"day": day, "month": month, "year": year},
            "source": "aladhan.com API",
        }


@router.get("/date/convert/hijri-to-gregorian", summary="Convert Hijri to Gregorian")
async def convert_hijri_to_gregorian(
    day: int = Query(..., description="Day", ge=1, le=30),
    month: int = Query(..., description="Hijri month", ge=1, le=12),
    year: int = Query(..., description="Hijri year"),
) -> dict[str, Any]:
    """
    Convert a Hijri date to Gregorian.

    Args:
        day: Day of Hijri month
        month: Hijri month
        year: Hijri year

    Returns:
        Gregorian date information
    """
    async with PrayerTimesAPIClient() as client:
        result = await client.get_gregorian_date_from_hijri(day, month, year)

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Invalid Hijri date",
            )

        return {
            "conversion": result,
            "input": {"day": day, "month": month, "year": year},
            "source": "aladhan.com API",
        }


@router.get("/qibla", summary="Get Qibla direction")
async def get_qibla_direction(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
) -> dict[str, Any]:
    """
    Get Qibla direction for a specific location.

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        Qibla direction in degrees
    """
    async with PrayerTimesAPIClient() as client:
        qibla = await client.get_qibla_direction(latitude, longitude)

        if not qibla:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch Qibla direction",
            )

        return {
            "qibla": qibla,
            "location": {"latitude": latitude, "longitude": longitude},
            "source": "aladhan.com API",
        }


@router.get("/asma-al-husna", summary="Get the 99 Names of Allah")
async def get_asma_al_husna() -> list[dict[str, Any]]:
    """
    Get the 99 Names of Allah (Asma Al-Husna).

    Returns:
        List of Allah's names with translations
    """
    async with PrayerTimesAPIClient() as client:
        names = await client.get_asma_al_husna()

        if not names:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch Asma Al-Husna",
            )

        return names
