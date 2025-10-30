"""
Cached Content Service

Retrieves Quran and Hadith content directly from Redis cache
instead of making external API calls. Provides instant responses.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from .cache_service import get_cache_service


class CachedContentService:
    """
    Service for retrieving Islamic content from Redis cache.
    
    This service provides instant access to Quran and Hadith data
    without external API calls, enabling faster LLM responses.
    """
    
    def __init__(self):
        """Initialize the cached content service."""
        self.cache = get_cache_service()
    
    async def get_surah_from_cache(
        self,
        surah_number: int,
        edition: str = "quran-uthmani"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a complete Surah from cache.
        
        Args:
            surah_number: Surah number (1-114)
            edition: Edition identifier
        
        Returns:
            Surah data or None if not cached
        
        Example:
            >>> service = CachedContentService()
            >>> fatiha = await service.get_surah_from_cache(1, "quran-uthmani")
            >>> print(fatiha['englishName'])
        """
        cache_key = f"quran_surah:{surah_number}:{edition}"
        result = await self.cache.get(cache_key)
        
        if result:
            logger.debug(f"✅ Retrieved Surah {surah_number} from cache")
        else:
            logger.debug(f"❌ Surah {surah_number} not in cache")
        
        return result
    
    async def get_ayah_from_cache(
        self,
        ayah_reference: str,
        edition: str = "quran-uthmani"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Ayah from cache.
        
        Args:
            ayah_reference: Reference like "2:255"
            edition: Edition identifier
        
        Returns:
            Ayah data or None if not cached
        """
        cache_key = f"quran_ayah:{ayah_reference}:{edition}"
        result = await self.cache.get(cache_key)
        
        if result:
            logger.debug(f"✅ Retrieved Ayah {ayah_reference} from cache")
        
        return result
    
    async def search_quran_in_cache(
        self,
        query: str,
        edition: str = "quran-uthmani",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for Quranic verses in cache.
        
        This performs a simple text search across all cached Surahs.
        For better semantic search, use the RAG system.
        
        Args:
            query: Search term (Arabic or English)
            edition: Edition to search
            limit: Maximum results
        
        Returns:
            List of matching ayahs
        """
        query_lower = query.lower()
        results = []
        
        # Search through all 114 Surahs
        for surah_num in range(1, 115):
            if len(results) >= limit:
                break
            
            surah = await self.get_surah_from_cache(surah_num, edition)
            if not surah:
                continue
            
            ayahs = surah.get('ayahs', [])
            for ayah in ayahs:
                text = ayah.get('text', '').lower()
                
                if query_lower in text or query in text:
                    results.append({
                        'surah_number': surah_num,
                        'surah_name': surah.get('englishName', ''),
                        'ayah_number': ayah.get('numberInSurah'),
                        'text': ayah.get('text'),
                        'ayah_data': ayah,
                    })
                    
                    if len(results) >= limit:
                        break
        
        logger.info(f"Found {len(results)} matching verses for '{query}'")
        return results
    
    async def get_hadith_from_cache(
        self,
        collection: str,
        hadith_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Hadith from cache.
        
        Args:
            collection: Collection ID (bukhari, muslim, malik, etc.)
            hadith_number: Hadith number
        
        Returns:
            Hadith data or None if not cached
        
        Example:
            >>> service = CachedContentService()
            >>> hadith = await service.get_hadith_from_cache("bukhari", 1)
            >>> print(hadith['arab'])
        """
        cache_key = f"hadith_single:{collection}:{hadith_number}"
        result = await self.cache.get(cache_key)
        
        if result:
            logger.debug(f"✅ Retrieved {collection} Hadith #{hadith_number} from cache")
        else:
            logger.debug(f"❌ {collection} Hadith #{hadith_number} not in cache")
        
        return result
    
    async def search_hadith_in_cache(
        self,
        query: str,
        collections: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for Hadiths in cache across collections.
        
        Args:
            query: Search term (Arabic or English)
            collections: List of collections to search (default: all)
            limit: Maximum results
        
        Returns:
            List of matching hadiths
        """
        if collections is None:
            collections = ["bukhari", "muslim", "malik", "abu-daud", "tirmidzi", "nasai", "ibnu-majah"]
        
        query_lower = query.lower()
        results = []
        
        # Define reasonable search ranges for each collection
        search_limits = {
            "bukhari": 1000,
            "muslim": 1000,
            "malik": 1587,  # Complete
            "abu-daud": 500,
            "tirmidzi": 500,
            "nasai": 500,
            "ibnu-majah": 500,
            "ahmad": 500,
            "darimi": 500,
        }
        
        for collection in collections:
            if len(results) >= limit:
                break
            
            search_limit = search_limits.get(collection, 500)
            
            for hadith_num in range(1, search_limit + 1):
                if len(results) >= limit:
                    break
                
                hadith = await self.get_hadith_from_cache(collection, hadith_num)
                if not hadith:
                    continue
                
                # Search in Arabic and English text
                arab_text = hadith.get('arab', '').lower()
                id_text = hadith.get('id', '').lower()  # Indonesian translation
                
                if query_lower in arab_text or query_lower in id_text or query in arab_text:
                    results.append({
                        'collection': collection,
                        'number': hadith.get('number'),
                        'arab': hadith.get('arab', ''),
                        'text': hadith.get('id', ''),  # Translation
                        'hadith_data': hadith,
                    })
        
        logger.info(f"Found {len(results)} matching hadiths for '{query}' in cache")
        return results
    
    async def get_maliki_hadiths_from_cache(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get Hadiths from Muwatta Malik (Maliki madhab source).
        
        Args:
            limit: Maximum hadiths to retrieve
        
        Returns:
            List of hadiths from Muwatta Malik
        """
        hadiths = []
        
        for hadith_num in range(1, min(limit + 1, 1588)):
            hadith = await self.get_hadith_from_cache("malik", hadith_num)
            if hadith:
                hadiths.append(hadith)
        
        logger.info(f"Retrieved {len(hadiths)} hadiths from Muwatta Malik")
        return hadiths
    
    async def get_context_for_question(
        self,
        question: str,
        include_quran: bool = True,
        include_hadith: bool = True,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Get relevant Quran and Hadith context for a question from cache.
        
        This is used by the LLM to provide context-aware answers
        without external API calls.
        
        Args:
            question: User's question
            include_quran: Include Quranic context
            include_hadith: Include Hadith context
            max_results: Max results per type
        
        Returns:
            Dictionary with quran_results and hadith_results
        """
        context = {
            'quran_results': [],
            'hadith_results': [],
            'source': 'redis_cache',
        }
        
        if include_quran:
            # Search Quran in both Arabic and English
            arabic_results = await self.search_quran_in_cache(
                question,
                edition="quran-uthmani",
                limit=max_results
            )
            context['quran_results'].extend(arabic_results)
        
        if include_hadith:
            # Search Hadith across major collections
            hadith_results = await self.search_hadith_in_cache(
                question,
                collections=["bukhari", "muslim", "malik"],
                limit=max_results
            )
            context['hadith_results'] = hadith_results
        
        logger.info(
            f"Retrieved context from cache: "
            f"{len(context['quran_results'])} Quran verses, "
            f"{len(context['hadith_results'])} Hadiths"
        )
        
        return context
    
    async def format_context_for_llm(
        self,
        context: Dict[str, Any],
        language: str = "arabic"
    ) -> str:
        """
        Format cached context for LLM prompt.
        
        Args:
            context: Context dictionary from get_context_for_question
            language: Target language
        
        Returns:
            Formatted context string
        """
        formatted_parts = []
        
        # Format Quran context
        if context.get('quran_results'):
            if language == "arabic":
                formatted_parts.append("## آيات قرآنية ذات صلة:")
            else:
                formatted_parts.append("## Relevant Quranic Verses:")
            
            for i, verse in enumerate(context['quran_results'][:3], 1):
                surah_name = verse.get('surah_name', '')
                ayah_num = verse.get('ayah_number', '')
                text = verse.get('text', '')
                formatted_parts.append(f"\n{i}. {surah_name} ({ayah_num}): {text}")
        
        # Format Hadith context
        if context.get('hadith_results'):
            if language == "arabic":
                formatted_parts.append("\n\n## أحاديث نبوية:")
            else:
                formatted_parts.append("\n\n## Relevant Hadiths:")
            
            for i, hadith in enumerate(context['hadith_results'][:3], 1):
                collection = hadith.get('collection', '').title()
                arab = hadith.get('arab', '')[:200]
                formatted_parts.append(f"\n{i}. [{collection}] {arab}...")
        
        return "\n".join(formatted_parts)


# Singleton instance
_cached_content_service: Optional[CachedContentService] = None


def get_cached_content_service() -> CachedContentService:
    """
    Get or create the global cached content service instance.
    
    Returns:
        CachedContentService instance
    """
    global _cached_content_service
    if _cached_content_service is None:
        _cached_content_service = CachedContentService()
    return _cached_content_service




