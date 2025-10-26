"""
Question Classifier - Determines if a question is about fiqh.

Only uses Maliki RAG for fiqh-related questions.
"""

from typing import Tuple


def wants_sources(question: str) -> bool:
    """
    Check if user explicitly wants to see sources/citations.
    
    Args:
        question: User's question
        
    Returns:
        True if user wants sources
    """
    source_keywords = [
        'source', 'sources', 'citation', 'reference', 'where from',
        'من أين', 'مصدر', 'مصادر', 'مرجع', 'دليل', 'أدلة',
        'show source', 'cite', 'proof', 'evidence',
    ]
    
    return any(keyword in question.lower() for keyword in source_keywords)


def is_fiqh_question(question: str) -> Tuple[bool, str]:
    """
    Determine if a question is about Islamic jurisprudence (fiqh).

    Args:
        question: User's question in Arabic or English

    Returns:
        Tuple of (is_fiqh: bool, category: str)
        
    Example:
        >>> is_fiqh_question("What is the ruling on wudu?")
        (True, "fiqh")
        
        >>> is_fiqh_question("Show me Surah Al-Fatiha")
        (False, "quran")
    """
    question_lower = question.lower()
    
    # Fiqh-related keywords in English
    fiqh_keywords_en = [
        'ruling', 'rulings', 'permissible', 'haram', 'halal', 'allowed',
        'forbidden', 'makruh', 'mustahab', 'wajib', 'fard', 'sunnah',
        'madhab', 'maliki', 'fiqh', 'jurisprudence', 'islamic law',
        'can i', 'is it allowed', 'is it permissible', 'what is the ruling',
        'how to pray', 'how to perform', 'wudu', 'ghusl', 'tayammum',
        'zakat', 'nisab', 'hajj', 'umrah', 'fast', 'fasting', 'sawm',
        'marriage', 'divorce', 'inheritance', 'business', 'transaction',
        'interest', 'riba', 'marriage contract', 'wali', 'mahr',
    ]
    
    # Fiqh-related keywords in Arabic
    fiqh_keywords_ar = [
        'حكم', 'أحكام', 'حلال', 'حرام', 'مكروه', 'مستحب', 'واجب', 'فرض',
        'سنة', 'مذهب', 'المالكية', 'فقه', 'شرع', 'يجوز', 'جائز', 'ممنوع',
        'كيف أصلي', 'كيفية', 'وضوء', 'غسل', 'تيمم', 'زكاة', 'نصاب',
        'حج', 'عمرة', 'صيام', 'صوم', 'رمضان', 'نكاح', 'زواج', 'طلاق',
        'ميراث', 'معاملات', 'بيع', 'شراء', 'ربا', 'فوائد', 'ولي', 'مهر',
    ]
    
    # Check for fiqh keywords
    if any(keyword in question_lower for keyword in fiqh_keywords_en):
        return (True, "fiqh")
    
    if any(keyword in question for keyword in fiqh_keywords_ar):
        return (True, "fiqh")
    
    # Check for Quran-related questions
    quran_keywords = [
        'surah', 'sura', 'ayah', 'verse', 'quran', 'qur\'an', 'recite',
        'سورة', 'آية', 'قرآن', 'اتل', 'قراءة', 'فاتحة', 'بقرة', 'إخلاص',
    ]
    
    if any(keyword in question_lower for keyword in quran_keywords):
        return (False, "quran")
    
    # Check for Hadith-related questions
    hadith_keywords = [
        'hadith', 'hadis', 'narration', 'prophet said', 'رسول الله',
        'حديث', 'أحاديث', 'روى', 'رواية', 'النبي', 'صلى الله عليه وسلم',
    ]
    
    if any(keyword in question_lower for keyword in hadith_keywords):
        return (False, "hadith")
    
    # Default: general Islamic question (not specifically fiqh)
    return (False, "general")


def get_response_instructions(is_fiqh: bool, category: str, language: str) -> str:
    """
    Get appropriate response instructions based on question type.

    Args:
        is_fiqh: Whether question is about fiqh
        category: Question category (fiqh, quran, hadith, general)
        language: Response language

    Returns:
        Instructions for the AI
    """
    if is_fiqh:
        if language == "arabic":
            return """You are an Islamic scholar specialized in MALIKI FIQH. 
Answer based on Maliki madhab positions and cite sources like Al-Risala and Mukhtasar Khalil when relevant."""
        else:
            return """You are an Islamic scholar specialized in MALIKI FIQH.
Answer based on Maliki madhab positions and cite sources when relevant."""
    
    else:
        # For non-fiqh questions, be a general Islamic scholar
        if language == "arabic":
            return """You are a knowledgeable Islamic scholar.
Answer based on Quran and authentic Hadith. Do NOT mention specific madhabs unless asked."""
        else:
            return """You are a knowledgeable Islamic scholar.
Answer based on Quran and authentic Hadith. Do NOT mention specific madhabs unless asked."""

