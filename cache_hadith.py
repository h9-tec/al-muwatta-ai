#!/usr/bin/env python3
"""
Hadith Cache Population Script

Pre-loads Hadith data into Redis cache from api.hadith.gading.dev.
Hadith content never changes, so it's cached for 365 days.

Usage:
    python cache_hadith.py                    # Cache all major collections
    python cache_hadith.py --full             # Cache complete Bukhari & Muslim
    python cache_hadith.py --malik-only       # Cache only Muwatta Malik (Maliki fiqh)
    python cache_hadith.py --collections bukhari muslim  # Specific collections
"""

import asyncio
import argparse
import httpx
from loguru import logger

from src.services.cache_service import get_cache_service


async def fetch_and_cache_batch(
    cache,
    client: httpx.AsyncClient,
    collection_id: str,
    start: int,
    end: int,
    base_url: str,
) -> int:
    """
    Fetch and cache a single batch of hadiths.
    
    Args:
        cache: Cache service instance
        client: HTTP client
        collection_id: Collection identifier
        start: Start index
        end: End index
        base_url: API base URL
    
    Returns:
        Number of entries cached (0 on failure)
    """
    try:
        response = await client.get(
            f"{base_url}/books/{collection_id}",
            params={"range": f"{start}-{end}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Cache the batch response
            cache_key = f"hadith_range:{collection_id}:{start}-{end}"
            await cache.set(cache_key, data.get("data"), ttl=31536000)
            cached_count = 1
            
            # Cache individual hadiths
            hadiths = data.get("data", {}).get("hadiths", [])
            for hadith in hadiths:
                hadith_num = hadith.get("number")
                if hadith_num:
                    cache_key = f"hadith_single:{collection_id}:{hadith_num}"
                    await cache.set(cache_key, hadith, ttl=31536000)
                    cached_count += 1
            
            return cached_count
        else:
            logger.warning(f"   ❌ Failed batch {start}-{end}: HTTP {response.status_code}")
            return 0
            
    except Exception as e:
        logger.error(f"   ❌ Error caching batch {start}-{end}: {str(e)[:100]}")
        return 0


async def cache_hadith_collection(
    cache,
    client: httpx.AsyncClient,
    collection_id: str,
    count: int,
    name: str
):
    """
    Cache hadiths from a specific collection using parallel batch processing.
    
    Args:
        cache: Cache service instance
        client: HTTP client
        collection_id: Collection identifier (e.g., 'bukhari')
        count: Number of hadiths to cache
        name: Display name of collection
    
    Returns:
        Number of hadiths cached
    """
    BASE_URL = "https://api.hadith.gading.dev"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📚 Caching {name}")
    logger.info(f"   Target: {count:,} hadiths")
    logger.info('='*60)
    
    batch_size = 50  # Fetch 50 at a time
    max_concurrent_batches = 10  # Process up to 10 batches in parallel
    
    # Create batch ranges
    batches = []
    for start in range(1, count + 1, batch_size):
        end = min(start + batch_size - 1, count)
        batches.append((start, end))
    
    total_cached = 0
    processed = 0
    
    # Process batches in parallel with concurrency limit
    for i in range(0, len(batches), max_concurrent_batches):
        batch_group = batches[i:i + max_concurrent_batches]
        
        # Create tasks for parallel execution
        tasks = [
            fetch_and_cache_batch(
                cache, client, collection_id, start, end, BASE_URL
            )
            for start, end in batch_group
        ]
        
        # Execute batches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"   ❌ Batch {batch_group[idx]} failed: {result}")
            else:
                total_cached += result
                processed += 1
        
        # Progress update
        if processed % 20 == 0 or processed == len(batches):
            progress_percent = (processed / len(batches)) * 100
            logger.info(f"   ✅ Progress: {processed}/{len(batches)} batches ({progress_percent:.1f}%)")
        
        # Small delay to avoid overwhelming the API
        await asyncio.sleep(0.2)
    
    logger.info(f"✅ {name}: {total_cached:,} entries cached successfully")
    return total_cached


async def main():
    """Main Hadith cache population."""
    
    parser = argparse.ArgumentParser(
        description="Cache Hadith data in Redis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cache_hadith.py                              # Default: Major collections
  python cache_hadith.py --full                       # Complete Bukhari & Muslim
  python cache_hadith.py --malik-only                 # Only Muwatta Malik
  python cache_hadith.py --collections bukhari muslim # Specific collections
  python cache_hadith.py --count 1000                 # Limit per collection
        """
    )
    parser.add_argument("--full", action="store_true", 
                       help="Cache complete Bukhari (6,638) & Muslim (4,930)")
    parser.add_argument("--all", action="store_true",
                       help="Cache ALL 9 collections COMPLETE (38,102 hadiths)")
    parser.add_argument("--malik-only", action="store_true",
                       help="Cache only Muwatta Malik (1,587 hadiths)")
    parser.add_argument("--collections", nargs="+",
                       help="Specific collections to cache")
    parser.add_argument("--count", type=int, default=500,
                       help="Max hadiths per collection (default: 500)")
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📚 HADITH CACHE POPULATION")
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
    
    # Define collections
    ALL_COLLECTIONS = {
        "bukhari": (6638, "Sahih Bukhari"),
        "muslim": (4930, "Sahih Muslim"),
        "malik": (1587, "Muwatta Malik"),
        "abu-daud": (4419, "Sunan Abu Daud"),
        "tirmidzi": (3625, "Jami' at-Tirmidhi"),
        "ibnu-majah": (4285, "Sunan Ibn Majah"),
        "nasai": (5364, "Sunan an-Nasa'i"),
        "ahmad": (4305, "Musnad Ahmad"),
        "darimi": (2949, "Sunan ad-Darimi"),
    }
    
    # Determine what to cache
    collections_to_cache = []
    
    if args.all:
        logger.info("Mode: ALL COLLECTIONS COMPLETE (38,102 hadiths)")
        collections_to_cache = [
            ("bukhari", 6638, "Sahih Bukhari (Complete)"),
            ("muslim", 4930, "Sahih Muslim (Complete)"),
            ("abu-daud", 4419, "Sunan Abu Daud (Complete)"),
            ("tirmidzi", 3625, "Jami' at-Tirmidhi (Complete)"),
            ("nasai", 5364, "Sunan an-Nasa'i (Complete)"),
            ("ibnu-majah", 4285, "Sunan Ibn Majah (Complete)"),
            ("malik", 1587, "Muwatta Malik (Complete)"),
            ("ahmad", 4305, "Musnad Ahmad (Complete)"),
            ("darimi", 2949, "Sunan ad-Darimi (Complete)"),
        ]
        
    elif args.malik_only:
        logger.info("Mode: Muwatta Malik only (Maliki fiqh)")
        collections_to_cache = [("malik", 1587, "Muwatta Malik (Complete)")]
        
    elif args.full:
        logger.info("Mode: FULL - Complete Bukhari & Muslim")
        collections_to_cache = [
            ("bukhari", 6638, "Sahih Bukhari (Complete)"),
            ("muslim", 4930, "Sahih Muslim (Complete)"),
            ("malik", 1587, "Muwatta Malik (Complete)"),
        ]
        
    elif args.collections:
        logger.info(f"Mode: Custom collections - {', '.join(args.collections)}")
        for coll in args.collections:
            if coll in ALL_COLLECTIONS:
                total, name = ALL_COLLECTIONS[coll]
                count = min(args.count, total)
                collections_to_cache.append((coll, count, name))
            else:
                logger.warning(f"Unknown collection: {coll}")
                
    else:
        # Default: Major collections with reasonable limits
        logger.info(f"Mode: DEFAULT - Major collections (top {args.count} each)")
        collections_to_cache = [
            ("bukhari", min(args.count, 6638), "Sahih Bukhari"),
            ("muslim", min(args.count, 4930), "Sahih Muslim"),
            ("malik", 1587, "Muwatta Malik (Complete)"),  # Always complete
            ("abu-daud", min(100, 4419), "Sunan Abu Daud"),
            ("tirmidzi", min(100, 3625), "Jami' at-Tirmidhi"),
            ("ibnu-majah", min(100, 4285), "Sunan Ibn Majah"),
        ]
    
    # Cache collections list
    logger.info("\n📋 Caching collections list...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("https://api.hadith.gading.dev/books")
            if response.status_code == 200:
                data = response.json()
                cache_key = "hadith_collections:gading"
                await cache.set(cache_key, data, ttl=31536000)
                logger.info(f"✅ Cached {len(data.get('data', []))} collection metadata")
        except Exception as e:
            logger.warning(f"Failed to cache collections list: {e}")
    
    # Cache each collection
    start_time = asyncio.get_event_loop().time()
    total_entries = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for collection_id, count, name in collections_to_cache:
            entries = await cache_hadith_collection(
                cache, client, collection_id, count, name
            )
            total_entries += entries
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    final_stats = cache.get_stats()
    
    # Summary
    print("\n" + "="*70)
    print("📊 HADITH CACHE SUMMARY")
    print("="*70)
    print(f"✅ Collections cached:       {len(collections_to_cache)}")
    print(f"✅ Total entries cached:     {total_entries:,}")
    print(f"⏱️  Time taken:               {elapsed_time:.1f} seconds")
    print(f"📊 Cache backend:            {'Redis (Persistent)' if cache.redis_enabled else 'In-Memory'}")
    print(f"💾 Cache operations:         {final_stats['sets']:,}")
    print(f"⚡ Average time/entry:       {(elapsed_time / total_entries * 1000):.2f}ms")
    print("="*70)
    
    print("\n📚 Cached Collections:")
    for collection_id, count, name in collections_to_cache:
        print(f"   • {name:<30} {count:>6,} hadiths")
    
    print("\n✨ Hadith cache population complete!")
    print("🚀 Hadith API requests will now be served from Redis cache!")
    print("💾 Data persists across application restarts\n")
    
    await cache.disconnect_redis()


if __name__ == "__main__":
    asyncio.run(main())

