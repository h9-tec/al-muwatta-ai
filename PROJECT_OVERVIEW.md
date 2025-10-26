# Nur Al-Ilm (نور العلم) - Islamic Knowledge Assistant

## 🌟 Project Overview

**Nur Al-Ilm** is a comprehensive Islamic knowledge platform that combines multiple authentic Islamic content APIs with Google Gemini AI to provide intelligent, contextual answers to Islamic questions. The project offers a unique, needed solution for Muslims seeking authentic Islamic knowledge with modern AI assistance.

## 🎯 Project Uniqueness

This project is **unique** because it:

1. **Aggregates Multiple Sources**: Combines Hadith collections, Quran translations, and prayer times into ONE unified API
2. **AI-Powered Insights**: Uses Google Gemini 2.0 to provide contextual explanations, tafsir, and scholarly insights
3. **Multilingual Support**: Works seamlessly in both Arabic and English
4. **Authentic Sources**: Only uses verified Islamic APIs (sunnah.com, alquran.cloud, aladhan.com)
5. **No Training Required**: Leverages pre-trained Gemini AI - no model training needed
6. **Comprehensive**: Covers Hadith, Quran, Prayer Times, and Islamic Calendar in one platform

## 🏗️ Architecture

```
nur-al-ilm/
├── src/
│   ├── api_clients/          # API client modules
│   │   ├── base_client.py    # Base HTTP client with error handling
│   │   ├── hadith_client.py  # Hadith collections API
│   │   ├── quran_client.py   # Quran API
│   │   └── prayer_times_client.py  # Prayer times & calendar
│   ├── services/
│   │   └── gemini_service.py # Google Gemini AI integration
│   ├── routers/              # FastAPI route handlers
│   │   ├── hadith_router.py
│   │   ├── quran_router.py
│   │   ├── prayer_times_router.py
│   │   └── ai_router.py
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── config.py             # Configuration management
│   └── main.py               # FastAPI application
├── tests/                    # Comprehensive test suite
│   ├── test_hadith_client.py
│   ├── test_quran_client.py
│   ├── test_prayer_times_client.py
│   └── test_gemini_service.py
├── requirements.txt          # Python dependencies
├── run.py                    # Quick start script
└── example_usage.py          # Usage examples
```

## 🔌 APIs Used

### 1. **Hadith API** (sunnah.com)
- **Collections**: Sahih Bukhari, Sahih Muslim, Sunan Abu Dawud, etc.
- **Features**: Search, browse by book, get specific Hadiths
- **Free**: Yes
- **Documentation**: https://sunnah.api-docs.io/

### 2. **Quran API** (alquran.cloud)
- **Editions**: 100+ translations and recitations
- **Features**: Search, access by Surah/Juz/Page, multiple editions
- **Free**: Yes
- **Documentation**: https://alquran.cloud/api

### 3. **Prayer Times API** (aladhan.com)
- **Features**: Prayer times, Islamic calendar, Qibla direction
- **Coverage**: Worldwide
- **Free**: Yes
- **Documentation**: https://aladhan.com/prayer-times-api

### 4. **Google Gemini AI**
- **Model**: Gemini 2.0 Flash
- **Features**: Text generation, Arabic understanding, contextual answers
- **Purpose**: Explanations, tafsir, Q&A

## ✨ Key Features

### 📚 Hadith Features
- Access multiple authentic Hadith collections
- Search in Arabic and English
- Browse by collection, book, and number
- AI-powered explanations of Hadiths
- Random Hadith generator

### 📖 Quran Features
- Complete Quran access with 100+ translations
- Search verses by topic or keywords
- Access by Surah, Juz, or Page
- AI-generated Tafsir (exegesis)
- Multiple editions simultaneously

### 🕌 Prayer & Calendar Features
- Accurate prayer times worldwide
- 13 different calculation methods
- Hijri/Gregorian calendar conversion
- Qibla direction calculator
- 99 Names of Allah (Asma Al-Husna)
- Monthly prayer calendars

### 🤖 AI Assistant Features
- Answer Islamic questions with references
- Generate thematic studies on any Islamic topic
- Provide Hadith authenticity verification guidance
- Contextual translation of Islamic texts
- Daily Islamic reminders
- Detailed tafsir of Quranic verses
- Comprehensive Hadith explanations

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd /home/hesham/hadith

# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt
```

### 2. Run Test Suite

```bash
# Run all API tests
python example_usage.py

# Or run pytest
pytest tests/ -v
```

### 3. Start API Server

```bash
# Start the FastAPI server
python run.py
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 📊 API Endpoints Summary

### Hadith Endpoints
- `GET /api/v1/hadith/collections` - List all collections
- `GET /api/v1/hadith/collections/{name}` - Get collection details
- `GET /api/v1/hadith/search` - Search Hadiths
- `GET /api/v1/hadith/random` - Get random Hadith
- `GET /api/v1/hadith/collections/{name}/hadiths/{number}` - Get specific Hadith

### Quran Endpoints
- `GET /api/v1/quran/editions` - List all editions
- `GET /api/v1/quran/surahs/{number}` - Get complete Surah
- `GET /api/v1/quran/ayahs/{reference}` - Get specific Ayah
- `GET /api/v1/quran/juz/{number}` - Get Juz
- `GET /api/v1/quran/search` - Search Quran

### Prayer Times Endpoints
- `GET /api/v1/prayer-times/timings` - Get prayer times by coordinates
- `GET /api/v1/prayer-times/timings/city` - Get by city name
- `GET /api/v1/prayer-times/calendar` - Monthly calendar
- `GET /api/v1/prayer-times/qibla` - Qibla direction
- `GET /api/v1/prayer-times/asma-al-husna` - 99 Names of Allah

### AI Assistant Endpoints
- `POST /api/v1/ai/ask` - Ask Islamic questions
- `POST /api/v1/ai/thematic-study` - Generate thematic studies
- `POST /api/v1/ai/translate` - Translate with context
- `POST /api/v1/ai/explain-verse` - Get Quranic tafsir
- `POST /api/v1/ai/explain-hadith` - Get Hadith explanation
- `GET /api/v1/ai/daily-reminder` - Daily Islamic reminder

## 🎨 Example Usage

### Python Example

```python
import httpx
import asyncio

async def get_surah_al_fatiha():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/quran/surahs/1",
            params={"edition": "en.sahih", "explain": True}
        )
        return response.json()

# Run
result = asyncio.run(get_surah_al_fatiha())
print(result)
```

### cURL Example

```bash
# Get prayer times for Makkah
curl "http://localhost:8000/api/v1/prayer-times/timings?latitude=21.3891&longitude=39.8579"

# Search Hadiths about prayer
curl "http://localhost:8000/api/v1/hadith/search?query=prayer&limit=5"

# Ask Islamic question
curl -X POST "http://localhost:8000/api/v1/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the pillars of Islam?", "language": "english"}'
```

## 🧪 Testing

Comprehensive test suite with 40+ tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_quran_client.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Configuration

All configuration is in `src/config.py` using environment variables:

```python
GEMINI_API_KEY=your_key_here  # Already configured
GEMINI_MODEL=gemini-2.0-flash-exp
DEBUG=True
LOG_LEVEL=INFO
```

## 📈 Performance

- **API Response Time**: < 2 seconds (depends on external APIs)
- **AI Response Time**: 2-5 seconds (Gemini generation)
- **Cache Support**: Planned for future versions
- **Rate Limiting**: Configurable

## 🎓 Use Cases

1. **Islamic Education**: Students learning about Islam
2. **Scholars**: Quick reference for Quranic verses and Hadiths
3. **Developers**: Build Islamic apps on top of this API
4. **Muslims Worldwide**: Access prayer times and Islamic content
5. **Research**: Analyze Islamic texts with AI assistance

## 🔮 Future Enhancements

- [ ] Redis caching for faster responses
- [ ] User authentication and personal bookmarks
- [ ] Audio recitations integration
- [ ] Mobile app (Flutter/React Native)
- [ ] Advanced semantic search
- [ ] More AI models support
- [ ] Offline mode support

## 📄 License

This project is for educational and Islamic knowledge purposes.

## 🤲 Credits

- **Hadith Data**: sunnah.com
- **Quran Data**: alquran.cloud
- **Prayer Times**: aladhan.com
- **AI**: Google Gemini
- **Built with**: FastAPI, Python, Love for Islam

---

**Made with ❤️ for the Muslim Ummah**

الحمد لله رب العالمين

