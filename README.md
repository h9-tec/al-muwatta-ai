# Al-Muwatta - Maliki Fiqh Assistant
## الموطأ - مساعد الفقه المالكي

<div align="center">

![Al-Muwatta Interface](screenshots/04-welcome-with-quick-actions.png)

**Specialized Islamic Knowledge Platform for Maliki Jurisprudence**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#features) • [Installation](#installation) • [Documentation](#documentation) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Al-Muwatta** is an Islamic knowledge platform specialized in Maliki jurisprudence, combining retrieval-augmented generation (RAG) with multiple LLM providers. Named after Imam Malik's foundational hadith compilation, the platform provides authenticated responses from classical Maliki texts.

**منصة الموطأ** هي منصة معرفة إسلامية متخصصة في الفقه المالكي، تجمع بين تقنية الاسترجاع المعزز (RAG) ومزودي نماذج لغوية متعددة. المنصة توفر إجابات موثقة من المصادر المالكية الأصيلة.

### Core Capabilities

**English:**
- Maliki fiqh knowledge base with 21+ authenticated texts
- Multi-provider LLM support (Ollama, OpenRouter, Groq, OpenAI, Claude, Gemini)
- Semantic search across Islamic content
- Comprehensive Islamic APIs integration
- RTL Arabic interface with dialect detection

**العربية:**
- قاعدة معرفية للفقه المالكي تضم 21+ نصاً موثقاً
- دعم متعدد لمزودي النماذج اللغوية (محلي ومستضاف)
- بحث دلالي عبر المحتوى الإسلامي
- تكامل شامل مع واجهات برمجة التطبيقات الإسلامية
- واجهة عربية بنظام RTL مع كشف تلقائي للهجة

---

## Features

### Maliki Fiqh Knowledge Base

**English:**
The platform implements RAG using Qdrant vector database containing authenticated Maliki texts:

- **Primary Sources**: Al-Risala (Ibn Abi Zayd), Mukhtasar Khalil, Al-Mudawwana
- **Coverage**: Taharah, Salah, Zakat, Sawm, Hajj, Muamalat, Family Law
- **Search**: Semantic search with 384-dimensional embeddings
- **Expandable**: Upload PDF/images to extend knowledge base

**العربية:**
تستخدم المنصة تقنية RAG مع قاعدة بيانات Qdrant تحتوي على نصوص مالكية موثقة:

- **المصادر الأساسية**: الرسالة (ابن أبي زيد)، مختصر خليل، المدونة
- **التغطية**: الطهارة، الصلاة، الزكاة، الصيام، الحج، المعاملات، الأحوال الشخصية
- **البحث**: بحث دلالي باستخدام متجهات 384 بُعداً
- **قابل للتوسع**: رفع ملفات PDF أو صور لتوسيع قاعدة المعرفة

### Multi-Provider LLM Support

**Supported Providers:**

| Provider | Type | API Required | Arabic Support |
|----------|------|--------------|----------------|
| Ollama | Local | No | Excellent (Qwen2.5) |
| OpenRouter | Cloud | Yes | Excellent |
| Groq | Cloud | Yes | Good |
| OpenAI | Cloud | Yes | Good |
| Claude | Cloud | Yes | Good |
| Gemini | Cloud | Yes | Excellent |

**مزودو الخدمة المدعومون:**
- **Ollama**: محلي ومجاني (يعمل على جهازك بدون إنترنت)
- **OpenRouter**: الوصول إلى 100+ نموذج
- **Groq**: سرعة استجابة عالية جداً
- **OpenAI**: GPT-4 وGPT-3.5
- **Claude**: Anthropic (جودة عالية)
- **Gemini**: Google (الافتراضي)

### Intelligent Question Classification

The system automatically detects question type and responds accordingly:

- **Fiqh questions**: Activates Maliki RAG, cites sources
- **Quran questions**: Provides Quranic content without madhab references
- **Hadith questions**: General hadith search and explanation
- **General questions**: Broad Islamic knowledge

**التصنيف الذكي للأسئلة:**
- **أسئلة فقهية**: يستخدم مصادر المذهب المالكي
- **أسئلة قرآنية**: يقدم المحتوى القرآني بدون ذكر المذاهب
- **أسئلة حديثية**: بحث وشرح الأحاديث
- **أسئلة عامة**: معلومات إسلامية شاملة

### Islamic Content Integration

**APIs Integrated:**
- **alquran.cloud**: 114 Surahs, 100+ translations, tafsir
- **aladhan.com**: Prayer times worldwide, Islamic calendar, Qibla direction
- **sunnah.com**: Hadith collections (requires API key)

**واجهات برمجة التطبيقات المدمجة:**
- **القرآن**: 114 سورة، 100+ ترجمة
- **أوقات الصلاة**: تغطية عالمية، التقويم الهجري، اتجاه القبلة
- **الأحاديث**: مجموعات متعددة

---

## Screenshots

### Welcome Interface

![Welcome Screen](screenshots/01-welcome-page.png)

**Features shown:**
- Bilingual welcome message (Arabic priority)
- Prayer times widget with geolocation
- Suggestion prompts
- Knowledge base statistics

---

### Maliki Fiqh Response with RAG

![Maliki Fiqh Answer](screenshots/02-arabic-chat-maliki-hand-placement.png)

**Technical demonstration:**
- RTL layout for Arabic
- Source attribution from Maliki texts
- Structured markdown rendering
- Context-aware response generation

---

### General Islamic Q&A

![Islamic Q&A](screenshots/03-arabic-conversation-parents.png)

**Capabilities:**
- Quranic verse citation
- Hadith references
- Comprehensive Islamic guidance
- Natural Arabic language processing

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  React 18 + TypeScript + Tailwind CSS                        │
│  • Chat Interface (RTL/LTR)                                  │
│  • Settings Modal                                            │
│  • File Upload Component                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│                   Backend Layer (FastAPI)                    │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ API Routers  │  │  Services   │  │  Data Clients    │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Data & AI Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │ Qdrant DB   │  │  LLM APIs    │  │  External APIs  │    │
│  │ (Vectors)   │  │  (Gemini/    │  │  (Quran, Prayer)│    │
│  │             │  │   Ollama)    │  │                 │    │
│  └─────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### RAG Pipeline

```
User Query
    ↓
Question Classification (fiqh vs non-fiqh)
    ↓
[If fiqh] → Vector Search (Qdrant) → Top 3 Maliki texts
    ↓
Context Injection + Prompt Engineering
    ↓
LLM Generation (Gemini/Ollama/etc.)
    ↓
Response (with optional source citations)
```

### Technology Stack

**Backend:**
```
- Python 3.12+
- FastAPI 0.111.0 (async web framework)
- Pydantic 2.9 (data validation)
- Qdrant 1.15+ (vector database)
- Sentence Transformers 5.1+ (embeddings)
- httpx 0.28+ (async HTTP client)
```

**Frontend:**
```
- React 18.3 (UI framework)
- TypeScript 5.6 (type safety)
- Vite 4.5 (build tool)
- Tailwind CSS 3.4 (styling)
- React Markdown (content rendering)
```

**AI/ML:**
```
- Google Gemini 2.0 Flash
- Ollama (local inference)
- Sentence Transformers: paraphrase-multilingual-MiniLM-L12-v2
- Vector Dimensions: 384
- Similarity: Cosine distance
```

---

## Installation

### Prerequisites

**Required:**
- Python 3.12 or higher
- Node.js 18 or higher
- 4GB RAM minimum
- Internet connection (for API access)

**Optional:**
- Ollama (for local LLM)
- CUDA GPU (for OCR)

### Quick Start

```bash
# Clone repository
git clone https://github.com/h9-tec/al-muwatta-ai.git
cd al-muwatta-ai

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Initialize vector database
python initialize_rag.py

# Start backend
python run.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Access application
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
```

### البدء السريع (عربي)

```bash
# استنساخ المستودع
git clone https://github.com/h9-tec/al-muwatta-ai.git
cd al-muwatta-ai

# إعداد الخادم
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# إعداد المتغيرات
cp .env.example .env
# أضف مفاتيح API في ملف .env

# تهيئة قاعدة البيانات
python initialize_rag.py

# تشغيل الخادم
python run.py

# في نافذة جديدة - إعداد الواجهة
cd frontend
npm install
npm run dev
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# LLM Provider Configuration
GEMINI_API_KEY=your_gemini_api_key
USE_LOCAL_LLM=False

# Ollama Configuration (optional)
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434

# Application Settings
APP_NAME=Al-Muwatta - الموطأ | Maliki Fiqh Assistant
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./al_muwatta.db
```

### Ollama Setup (Local LLM)

**English:**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model (recommended for Arabic)
ollama pull qwen2.5:7b

# Start Ollama server
ollama serve

# Test
python test_ollama.py
```

**العربية:**

```bash
# تثبيت Ollama
curl -fsSL https://ollama.com/install.sh | sh

# تحميل النموذج (موصى به للعربية)
ollama pull qwen2.5:7b

# تشغيل الخادم
ollama serve

# اختبار
python test_ollama.py
```

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### AI Assistant

```http
POST /api/v1/ai/ask
Content-Type: application/json

{
  "question": "What are the pillars of Islam?",
  "language": "english"
}
```

#### Quran Access

```http
GET /api/v1/quran/surahs/1?edition=en.sahih
GET /api/v1/quran/ayahs/2:255
GET /api/v1/quran/search?query=patience
```

#### Prayer Times

```http
GET /api/v1/prayer-times/timings?latitude=21.3891&longitude=39.8579
GET /api/v1/prayer-times/timings/city?city=Cairo&country=Egypt
GET /api/v1/prayer-times/qibla?latitude=40.7128&longitude=-74.0060
```

#### Knowledge Base Management

```http
POST /api/v1/upload/book-pdf
POST /api/v1/upload/book-image
GET /api/v1/upload/knowledge-base/stats
```

#### Provider Settings

```http
GET /api/v1/settings/providers
POST /api/v1/settings/providers/{provider}/models
POST /api/v1/settings/test-connection
```

---

## Development

### Project Structure

```
al-muwatta-ai/
├── src/                          # Backend source
│   ├── api_clients/              # External API integrations
│   ├── routers/                  # API endpoints
│   ├── services/                 # Business logic
│   │   ├── gemini_service.py     # Gemini integration
│   │   ├── ollama_service.py     # Ollama integration
│   │   ├── multi_llm_service.py  # Multi-provider handler
│   │   ├── rag_service.py        # RAG implementation
│   │   └── ocr_service.py        # OCR processing
│   ├── models/                   # Pydantic schemas
│   ├── utils/                    # Utilities
│   ├── config.py                 # Configuration
│   └── main.py                   # FastAPI application
├── frontend/                     # Frontend source
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utilities and API client
│   │   └── App.tsx               # Main application
├── tests/                        # Test suite
├── scrapers/                     # Web scraping tools
├── qdrant_db/                    # Vector database storage
└── docs/                         # Documentation
```

### Running Tests

```bash
# Backend tests
source venv/bin/activate
pytest tests/ -v --cov=src

# Coverage report
pytest tests/ --cov=src --cov-report=html
```

### Adding Maliki Content

**Method 1: Direct Upload via UI**
1. Access application at localhost:5173
2. Use upload button to submit PDF or images
3. System extracts text and adds to vector database

**Method 2: Programmatic Addition**

```python
from src.services.rag_service import MalikiFiqhRAG

rag = MalikiFiqhRAG()
rag.add_document(
    text="Your Maliki fiqh content here...",
    metadata={
        "topic": "Topic Name",
        "category": "salah",  # or zakat, sawm, etc.
        "source": "Book Name",
        "references": "Al-Risala, Mukhtasar Khalil",
    }
)
```

---

## Deployment

### Production Backend

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn src.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Production Frontend

```bash
cd frontend
npm run build
npx serve -s dist -l 3000
```

### Docker (Coming Soon)

```bash
docker-compose up -d
```

---

## Data Sources

### Primary Maliki Texts

**Current knowledge base includes:**
- Al-Risala - Ibn Abi Zayd al-Qayrawani
- Mukhtasar Khalil - Khalil ibn Ishaq
- Al-Mudawwana - Imam Malik and students
- Al-Muwatta - Imam Malik ibn Anas
- Bidayat al-Mujtahid - Ibn Rushd

### API Providers

| API | Endpoint | Documentation |
|-----|----------|---------------|
| Quran | api.alquran.cloud | https://alquran.cloud/api |
| Prayer Times | api.aladhan.com | https://aladhan.com/prayer-times-api |
| Hadith | api.sunnah.com | https://sunnah.api-docs.io |

---

## Performance Metrics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Vector Search | <200ms | Local Qdrant |
| LLM Response | 2-5s | Varies by provider |
| Quran API | <1s | Cached by provider |
| Prayer Times | <1s | Global CDN |

**Scalability:**
- Concurrent users: 100+ (FastAPI async)
- Vector search: Sub-second for 1M+ documents
- Database: Qdrant horizontal scaling supported

---

## Security

### API Key Management

All sensitive credentials stored in `.env` file:
- File is gitignored
- Never committed to repository
- Environment-specific configuration

### Data Privacy

- No user data stored by default
- Chat history: Client-side localStorage only
- Uploaded files: Local storage
- External APIs: Subject to their terms

---

## Contributing

### How to Contribute

**Code Contributions:**
1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

**Content Contributions:**
- Upload Maliki fiqh texts via UI
- Submit authenticated content via API
- Verify sources before submission

**Guidelines:**
- Follow PEP 8 (Python), ESLint (TypeScript)
- Add tests for new features
- Update documentation
- Verify Islamic authenticity of content

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### المساهمة (عربي)

**كيفية المساهمة:**
- إضافة محتوى فقهي مالكي موثق
- تحسين الكود البرمجي
- الإبلاغ عن المشاكل
- ترجمة الوثائق

انظر [CONTRIBUTING.md](CONTRIBUTING.md) للتفاصيل.

---

## Roadmap

### Completed
- [x] Core platform with FastAPI + React
- [x] Maliki fiqh RAG system (21+ documents)
- [x] Multi-provider LLM support
- [x] Arabic RTL interface
- [x] Question classification
- [x] File upload and OCR
- [x] Session persistence

### In Progress
- [ ] User authentication
- [ ] Advanced analytics
- [ ] Mobile application

### Planned
- [ ] Multi-madhab support (Shafi'i, Hanafi, Hanbali)
- [ ] Voice input/output
- [ ] Advanced caching layer
- [ ] Docker deployment
- [ ] Cloud hosting

---

## Troubleshooting

### Backend Issues

```bash
# Check logs
tail -f logs/backend_stable.log

# Verify imports
python -c "from src.main import app; print('OK')"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend Issues

```bash
# Check logs
tail -f logs/frontend.log

# Clear cache
cd frontend
rm -rf node_modules/.vite dist
npm install
```

### RAG Database

```bash
# Reinitialize
python initialize_rag.py

# Check status
curl http://localhost:8000/api/v1/upload/knowledge-base/stats
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- FastAPI: MIT
- React: MIT
- Qdrant: Apache 2.0
- Sentence Transformers: Apache 2.0

---

## Acknowledgments

### Islamic Scholarship
- Imam Malik ibn Anas (founder of Maliki madhab)
- Ibn Abi Zayd al-Qayrawani (Al-Risala)
- Khalil ibn Ishaq (Mukhtasar Khalil)
- Islamic scholars preserving knowledge

### Technical Foundation
- Google (Gemini API)
- Qdrant (vector database)
- Hugging Face (transformer models)
- Open source community

---

## Contact

**Repository**: https://github.com/h9-tec/al-muwatta-ai  
**Issues**: https://github.com/h9-tec/al-muwatta-ai/issues  
**Discussions**: https://github.com/h9-tec/al-muwatta-ai/discussions  
**Maintainer**: [@h9-tec](https://github.com/h9-tec)

---

## Citation

If you use this project in research or production:

```bibtex
@software{almuwatta2025,
  title = {Al-Muwatta: Maliki Fiqh Assistant with RAG},
  author = {Hesham Haroon},
  year = {2025},
  url = {https://github.com/h9-tec/al-muwatta-ai},
  note = {Islamic knowledge platform specialized in Maliki jurisprudence}
}
```

---

<div align="center">

**Built for the Muslim Ummah**

**الحمد لله رب العالمين**

*"Indeed, in the remembrance of Allah do hearts find rest." (Quran 13:28)*

</div>
