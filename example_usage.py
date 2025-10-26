"""
Nur Al-Ilm - Example Usage Script

This script demonstrates how to use all the API clients and AI services.
Run this to test all functionality.
"""

import asyncio
from loguru import logger

from src.api_clients import (
    HadithAPIClient,
    QuranAPIClient,
    PrayerTimesAPIClient,
)
from src.services import GeminiService


async def test_hadith_api():
    """Test Hadith API functionality."""
    print("\n" + "="*60)
    print("🕌 Testing Hadith API")
    print("="*60)

    async with HadithAPIClient() as client:
        # Get collections
        print("\n📚 Fetching Hadith collections...")
        collections = await client.get_collections()
        if collections:
            print(f"✅ Found {len(collections)} collections")
        else:
            print("⚠️  Hadith API may be unavailable")

        # Search Hadiths
        print("\n🔍 Searching for Hadiths about 'prayer'...")
        results = await client.search_hadith("prayer", limit=3)
        if results.get("data"):
            print(f"✅ Found {len(results['data'])} Hadiths")
        else:
            print("⚠️  No results or API unavailable")

        # Get random Hadith
        print("\n🎲 Fetching random Hadith...")
        random_hadith = await client.get_random_hadith()
        if random_hadith:
            print("✅ Random Hadith retrieved")
        else:
            print("⚠️  Random Hadith API may be unavailable")


async def test_quran_api():
    """Test Quran API functionality."""
    print("\n" + "="*60)
    print("📖 Testing Quran API")
    print("="*60)

    async with QuranAPIClient() as client:
        # Get Surah Al-Fatiha
        print("\n📜 Fetching Surah Al-Fatiha...")
        surah = await client.get_surah(1, edition="en.sahih")
        if surah:
            print(f"✅ Retrieved: {surah.get('englishName', 'Al-Fatiha')}")
            print(f"   Number of verses: {len(surah.get('ayahs', []))}")

            # Print first verse
            if surah.get("ayahs"):
                first_ayah = surah["ayahs"][0]
                print(f"\n   First verse: {first_ayah.get('text', '')[:100]}...")
        else:
            print("❌ Failed to retrieve Surah")

        # Get Ayat al-Kursi
        print("\n🌟 Fetching Ayat al-Kursi (2:255)...")
        ayat_kursi = await client.get_ayah("2:255", edition="en.sahih")
        if ayat_kursi:
            print("✅ Retrieved Ayat al-Kursi")
            print(f"   Translation: {ayat_kursi.get('text', '')[:80]}...")
        else:
            print("❌ Failed to retrieve Ayat al-Kursi")

        # Get available editions
        print("\n📚 Fetching available editions...")
        editions = await client.get_editions(language="en")
        if editions:
            print(f"✅ Found {len(editions)} English editions")
            print(f"   Examples: {', '.join([e['identifier'] for e in editions[:3]])}")
        else:
            print("❌ Failed to retrieve editions")


async def test_prayer_times_api():
    """Test Prayer Times API functionality."""
    print("\n" + "="*60)
    print("🕌 Testing Prayer Times API")
    print("="*60)

    async with PrayerTimesAPIClient() as client:
        # Get prayer times for Makkah
        print("\n🕋 Fetching prayer times for Makkah...")
        timings = await client.get_timings(21.3891, 39.8579)
        if timings:
            print("✅ Prayer times retrieved:")
            prayer_times = timings.get("timings", {})
            print(f"   Fajr: {prayer_times.get('Fajr')}")
            print(f"   Dhuhr: {prayer_times.get('Dhuhr')}")
            print(f"   Asr: {prayer_times.get('Asr')}")
            print(f"   Maghrib: {prayer_times.get('Maghrib')}")
            print(f"   Isha: {prayer_times.get('Isha')}")
        else:
            print("❌ Failed to retrieve prayer times")

        # Get current date
        print("\n📅 Fetching current Islamic date...")
        date_info = await client.get_current_date()
        if date_info:
            hijri = date_info.get("hijri", {})
            gregorian = date_info.get("gregorian", {})
            print(f"✅ Today's date:")
            print(f"   Hijri: {hijri.get('date', '')}")
            print(f"   Gregorian: {gregorian.get('date', '')}")
        else:
            print("❌ Failed to retrieve date")

        # Get Asma Al-Husna
        print("\n🤲 Fetching 99 Names of Allah...")
        names = await client.get_asma_al_husna()
        if names:
            print(f"✅ Retrieved {len(names)} names")
            print(f"   First name: {names[0].get('name', '')} - {names[0].get('en', {}).get('meaning', '')}")
        else:
            print("❌ Failed to retrieve Asma Al-Husna")


async def test_gemini_ai():
    """Test Google Gemini AI functionality."""
    print("\n" + "="*60)
    print("🤖 Testing Google Gemini AI")
    print("="*60)

    gemini = GeminiService()

    # Answer Islamic question
    print("\n❓ Asking: 'What are the five pillars of Islam?'")
    answer = await gemini.answer_islamic_question(
        "What are the five pillars of Islam?",
        language="english",
    )
    if answer:
        print("✅ Answer generated:")
        print(f"   {answer[:200]}...\n")
    else:
        print("❌ Failed to generate answer")

    # Generate daily reminder
    print("🌅 Generating daily reminder on 'gratitude'...")
    reminder = await gemini.generate_daily_reminder(
        theme="gratitude",
        language="english",
    )
    if reminder:
        print("✅ Daily reminder:")
        print(f"   {reminder[:200]}...\n")
    else:
        print("❌ Failed to generate reminder")

    # Translate Islamic text
    print("🔄 Translating 'الحمد لله' (Al-Hamdu Lillah)...")
    translation = await gemini.translate_with_context(
        "الحمد لله",
        source_lang="arabic",
        target_lang="english",
    )
    if translation:
        print("✅ Translation:")
        print(f"   {translation[:200]}...\n")
    else:
        print("❌ Failed to translate")

    # Explain Hadith
    hadith_text = "إنما الأعمال بالنيات"
    print(f"📝 Explaining Hadith: '{hadith_text}'...")
    explanation = await gemini.explain_hadith(hadith_text, language="english")
    if explanation:
        print("✅ Explanation generated:")
        print(f"   {explanation[:200]}...\n")
    else:
        print("❌ Failed to explain Hadith")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🌟 Nur Al-Ilm - نور العلم")
    print("   Islamic Knowledge Assistant - Test Suite")
    print("="*60)

    try:
        # Test all APIs
        await test_quran_api()
        await test_prayer_times_api()
        await test_hadith_api()
        await test_gemini_ai()

        print("\n" + "="*60)
        print("✨ All tests completed!")
        print("="*60)
        print("\n🚀 You can now start the API server with:")
        print("   python run.py")
        print("\n📖 Or run tests with:")
        print("   pytest tests/ -v")
        print("\n")

    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

