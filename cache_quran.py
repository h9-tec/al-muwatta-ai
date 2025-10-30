#!/usr/bin/env python3
"""
Quran Cache Population Script

Pre-loads all Quran data into Redis cache.
Quran content never changes, so it's cached for 365 days.

Usage:
    python cache_quran.py              # Cache all 114 Surahs
    python cache_quran.py --full       # Include all editions
    python cache_quran.py --minimal    # Cache only top 20 Surahs
"""

import asyncio
import argparse
import httpx
from loguru import logger

from src.services.cache_service import get_cache_service


async def cache_all_quran(cache, editions: list = None, minimal: bool = False):
    """
    Cache all Quran data.
    
    Args:
        cache: Cache service instance
        editions: List of editions to cache (default: Arabic + English)
        minimal: If True, only cache first 20 Surahs
    """
    if editions is None:
        editions = ["quran-uthmani", "en.sahih"]
    
    total_cached = 0
    surahs_to_cache = 20 if minimal else 114
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        logger.info(f"📖 Caching {surahs_to_cache} Surahs in {len(editions)} edition(s)...")
        
        for edition in editions:
            edition_name = "Arabic" if "uthmani" in edition else "English"
            logger.info(f"\n{'='*60}")
            logger.info(f"Caching all Surahs - {edition_name} ({edition})")
            logger.info('='*60)
            
            for surah_num in range(1, surahs_to_cache + 1):
                try:
                    response = await client.get(
                        f"https://api.alquran.cloud/v1/surah/{surah_num}/{edition}"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        surah_data = data.get("data")
                        
                        # Cache with key matching the @cached decorator pattern
                        cache_key = f"quran_surah:{surah_num}:{edition}"
                        await cache.set(cache_key, surah_data, ttl=31536000)  # 365 days
                        total_cached += 1
                        
                        if surah_num % 10 == 0:
                            surah_name = surah_data.get('englishName', f'Surah {surah_num}')
                            logger.info(f"   ✅ {surah_num}/114 - {surah_name}")
                    else:
                        logger.warning(f"   ❌ Failed to fetch Surah {surah_num}: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"   ❌ Error caching Surah {surah_num}: {e}")
                    continue
            
            logger.info(f"✅ Completed {edition_name}: {surahs_to_cache} Surahs cached")
        
        # Cache famous verses
        logger.info(f"\n{'='*60}")
        logger.info("Caching famous verses...")
        logger.info('='*60)
        
        famous_verses = [
            ("2:255", "Ayat al-Kursi"),
            ("1:1", "Al-Fatiha verse 1"),
            ("112:1", "Al-Ikhlas"),
            ("113:1", "Al-Falaq"),
            ("114:1", "An-Nas"),
            ("36:1", "Ya-Sin"),
            ("67:1", "Al-Mulk"),
            ("18:10", "Al-Kahf - Friday reading"),
        ]
        
        for verse_ref, description in famous_verses:
            for edition in editions:
                try:
                    response = await client.get(
                        f"https://api.alquran.cloud/v1/ayah/{verse_ref}/{edition}"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        cache_key = f"quran_ayah:{verse_ref}:{edition}"
                        await cache.set(cache_key, data.get("data"), ttl=31536000)
                        total_cached += 1
                        logger.info(f"   ✅ {description} ({edition})")
                        
                except Exception as e:
                    logger.warning(f"   ❌ Error caching {verse_ref}: {e}")
    
    return total_cached


async def main():
    """Main Quran cache population."""
    
    parser = argparse.ArgumentParser(description="Cache Quran data in Redis")
    parser.add_argument("--full", action="store_true", help="Cache multiple editions")
    parser.add_argument("--minimal", action="store_true", help="Cache only top 20 Surahs")
    parser.add_argument("--editions", nargs="+", help="Specific editions to cache")
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📖 QURAN CACHE POPULATION")
    print("="*70 + "\n")
    
    # Initialize cache
    cache = get_cache_service()
    await cache.connect_redis()
    
    if not cache.redis_enabled:
        print("⚠️  WARNING: Redis not available, using in-memory cache")
        print("   Cache will be lost when this script exits!")
        print("   Add REDIS_URL to .env for persistent caching\n")
    else:
        print("✅ Redis connected: Persistent cache enabled\n")
    
    # Determine editions to cache
    editions = args.editions
    if not editions:
        if args.full:
            editions = [
                "quran-uthmani",      # Arabic Uthmani
                "en.sahih",           # Sahih International
                "en.pickthall",       # Pickthall
                "ar.muyassar",        # Arabic simplified
            ]
        else:
            editions = ["quran-uthmani", "en.sahih"]
    
    logger.info(f"Editions to cache: {', '.join(editions)}")
    
    # Cache Quran
    initial_stats = cache.get_stats()
    start_time = asyncio.get_event_loop().time()
    
    total_cached = await cache_all_quran(cache, editions, args.minimal)
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    final_stats = cache.get_stats()
    
    # Summary
    print("\n" + "="*70)
    print("📊 QURAN CACHE SUMMARY")
    print("="*70)
    print(f"✅ Total entries cached:    {total_cached}")
    print(f"⏱️  Time taken:              {elapsed_time:.1f} seconds")
    print(f"📈 Cache size:               {final_stats['memory_cache_size']} entries")
    print(f"💾 Cache operations:         {final_stats['sets']} sets")
    print(f"📊 Cache backend:            {'Redis (Persistent)' if cache.redis_enabled else 'In-Memory (Temporary)'}")
    print(f"⚡ Average time/entry:       {(elapsed_time / total_cached * 1000):.2f}ms")
    print("="*70)
    
    print("\n✨ Quran cache population complete!")
    print("🚀 Quran API requests will now be served from cache!\n")
    
    await cache.disconnect_redis()


if __name__ == "__main__":
    asyncio.run(main())




