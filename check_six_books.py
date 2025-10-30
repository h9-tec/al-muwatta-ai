#!/usr/bin/env python3
"""
Check for Al-Kutub al-Sittah (الكتب الستة) - The Six Canonical Hadith Books

Verifies which APIs have all six major Sunni hadith collections.
"""

import asyncio
import httpx


async def check_six_books():
    """Check for the six canonical books."""
    
    print('\n' + '='*70)
    print('📚 AL-KUTUB AL-SITTAH (الكتب الستة)')
    print('   The Six Canonical Hadith Books')
    print('='*70 + '\n')
    
    # The six canonical books
    six_books = [
        ('bukhari', 'Sahih Bukhari', 'صحيح البخاري'),
        ('muslim', 'Sahih Muslim', 'صحيح مسلم'),
        ('abu-daud', 'Sunan Abu Dawud', 'سنن أبي داود'),
        ('tirmidzi', 'Jami` at-Tirmidhi', 'جامع الترمذي'),
        ('nasai', 'Sunan an-Nasa\'i', 'سنن النسائي'),
        ('ibnu-majah', 'Sunan Ibn Majah', 'سنن ابن ماجه'),
    ]
    
    print('The Six Canonical Books:')
    print('-'*70)
    for i, (book_id, name, arabic) in enumerate(six_books, 1):
        print(f'{i}. {name:<25} {arabic}')
    print()
    
    # Test api.hadith.gading.dev
    BASE_URL = 'https://api.hadith.gading.dev'
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        print('🔍 Testing api.hadith.gading.dev...')
        print('-'*70)
        
        response = await client.get(f'{BASE_URL}/books')
        result = response.json()
        available_books = result.get('data', [])
        
        print(f'✅ API Response: {result.get("message")}\n')
        
        # Check which of the six books are available
        available_ids = {book['id']: book for book in available_books}
        
        found_count = 0
        total_hadiths = 0
        
        print('📖 Checking for the Six Books:')
        print('-'*70)
        
        for book_id, name, arabic in six_books:
            if book_id in available_ids:
                book_info = available_ids[book_id]
                count = book_info['available']
                total_hadiths += count
                print(f'✅ {name:<25} ({count:>6,} hadiths) {arabic}')
                found_count += 1
            else:
                print(f'❌ {name:<25} Not available')
        
        print('-'*70)
        print(f'   TOTAL from Six Books:     {total_hadiths:>6,} hadiths')
        print()
        
        print('='*70)
        if found_count == 6:
            print('🎉 PERFECT! All 6 canonical books (الكتب الستة) are available!')
            print(f'📊 Total: {total_hadiths:,} authentic hadiths')
        else:
            print(f'⚠️  Found {found_count}/6 books')
        print('='*70)
        
        # Show all available collections
        print('\n📚 Complete List of Available Collections:')
        print('-'*70)
        
        six_book_ids = {b[0] for b in six_books}
        
        for book in available_books:
            is_canonical = '⭐' if book['id'] in six_book_ids else '  '
            print(f'{is_canonical} {book["name"]:<25} ({book["id"]:<15}) - {book["available"]:>6,} hadiths')
        
        print()
        print('⭐ = Part of the six canonical books (الكتب الستة)')
        print()
        
        # Get Redis cache size
        import redis.asyncio as aioredis
        try:
            redis_client = await aioredis.from_url('redis://localhost:6379/0')
            info = await redis_client.info('memory')
            dbsize = await redis_client.dbsize()
            
            print('='*70)
            print('💾 CURRENT REDIS CACHE')
            print('='*70)
            print(f'Memory used:              {info["used_memory_human"]}')
            print(f'Total keys cached:        {dbsize:,}')
            print('='*70)
            
            await redis_client.close()
        except Exception as e:
            print(f'Note: Could not get Redis stats - {e}')
        
        print('\n🔗 API Information:')
        print(f'   Base URL:  {BASE_URL}')
        print('   Free:      ✅ No API key required')
        print('   Arabic:    ✅ Full Arabic text included')
        print('   Reliable:  ✅ Hosted on Vercel (fast CDN)')
        print()


if __name__ == '__main__':
    asyncio.run(check_six_books())




