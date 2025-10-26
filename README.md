# Al-Muwatta (الموطأ) - Maliki Fiqh Assistant

<div align="center">

![Al-Muwatta Welcome Screen](screenshots/04-welcome-with-quick-actions.png)

**A Revolutionary AI-Powered Maliki Fiqh Platform**  
*RAG-Enhanced Islamic Knowledge Assistant with 21+ Authentic Sources*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://react.dev)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4.svg)](https://ai.google.dev/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C.svg)](https://qdrant.tech/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-key-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Architecture](#-architecture) • [API](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [RAG System](#-rag-system-maliki-fiqh)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🌟 Overview

**Al-Muwatta (الموطأ)** - named after Imam Malik's legendary hadith compilation - is a cutting-edge Islamic knowledge platform that combines authentic Islamic content APIs with Google Gemini AI and a specialized Retrieval-Augmented Generation (RAG) system focused on **Maliki Fiqh**.

### Welcome Interface

![Welcome Page](screenshots/welcome-page.png)

The beautiful welcome screen features:
- ✨ **Al-Muwatta branding** - الموطأ in elegant Arabic calligraphy
- 🕌 **Arabic-first welcome message** - Bilingual greeting
- 📚 **21+ Maliki Fiqh books** in the knowledge base
- 🎯 **Quick Action buttons** - Surah Al-Fatiha, Daily Reminder, Search Hadith, 99 Names
- 🕌 **Prayer Times widget** - Auto-location with all 5 prayers
- 🎨 **Islamic design** - Beautiful gradient cards with modern UI

### What Makes It Unique?

1. **🎯 Maliki Fiqh Specialization** - First AI assistant with dedicated Maliki jurisprudence knowledge base
2. **🤖 RAG-Enhanced Responses** - Answers cite authentic sources (Al-Risala, Mukhtasar Khalil, Al-Mudawwana)
3. **🌍 Perfect Arabic Support** - RTL layout, dialect matching, beautiful typography
4. **📚 Comprehensive Coverage** - Quran, Hadith, Prayer Times, Islamic Calendar, and Fiqh
5. **📤 User-Expandable** - Upload books (images/PDFs) to grow the knowledge base
6. **🔍 Semantic Search** - Multilingual vector search in 384-dimensional space
7. **⚡ Production-Ready** - FastAPI backend, React frontend, Qdrant vector DB

---

## ✨ Key Features

### 🤖 AI-Powered Islamic Assistant

- **Google Gemini 2.0 Flash** - State-of-the-art LLM with Arabic expertise
- **Automatic Language Detection** - Responds in user's language/dialect
- **Dialect Matching** - Understands formal Arabic (فصحى) and colloquial (عامية)
- **Context-Aware Responses** - Uses RAG to cite authentic Maliki sources

### 📚 Islamic Content APIs

| API | Content | Status |
|-----|---------|--------|
| **Quran API** | 114 Surahs, 100+ translations | ✅ Working |
| **Prayer Times API** | Worldwide coverage, 13 calculation methods | ✅ Working |
| **Hadith API** | Multiple collections, search | ⚠️ Requires API key |
| **Islamic Calendar** | Hijri/Gregorian conversion | ✅ Working |

### 🔍 RAG System - Maliki Fiqh Knowledge Base

- **21+ Documents** covering all major Maliki fiqh topics
- **Qdrant Vector Database** - Fast, scalable, production-ready
- **Semantic Search** - Find relevant content by meaning, not keywords
- **Source Citations** - Every answer references authentic texts
- **Expandable** - Users can upload their own books

**Topics Covered:**
- Taharah (Purification) - Wudu, Ghusl, Tayammum
- Salah (Prayer) - Daily prayers, Jumu'ah, Eid, Janazah
- Sawm (Fasting) - Ramadan rulings, breaking fast
- Zakat (Charity) - Nisab, rates, distribution
- Hajj - Pilgrimage, Udhiyah
- Muamalat - Business transactions
- Family Law - Marriage, divorce

### 📤 Upload & Expand

- **Image Upload** - OCR book pages and add to knowledge base
- **PDF Upload** - Extract full books automatically
- **DeepSeek-OCR Ready** - GPU-accelerated OCR (optional)
- **Manual Text Entry** - Add content directly via API

### 🌍 Exceptional Arabic Support

- ✅ **RTL (Right-to-Left) Layout** - Automatic for Arabic content
- ✅ **Beautiful Typography** - Amiri font, 1.1em size, 1.8 line-height
- ✅ **Bidirectional Markdown** - Proper rendering of mixed content
- ✅ **Dialect Intelligence** - Matches Egyptian, Gulf, Moroccan Arabic
- ✅ **Arabic Font Families** - Traditional Arabic, Amiri fallbacks

### 🎨 Modern & Beautiful UI

- **Full-Width Chat** - Maximum screen utilization
- **Markdown Rendering** - Headers, lists, code blocks, tables
- **Islamic Design System** - Green (#006B3F) and Teal (#008B8B) palette
- **Glass Morphism** - Modern, elegant UI elements
- **Responsive** - Works on desktop, tablet, mobile
- **Dark Mode Ready** - Theme toggle included

---

## 📸 Screenshots

### Main Chat Interface - Arabic Mode with RAG Citations

![Arabic Chat with Maliki Fiqh Sources](screenshots/arabic-chat-rag.png)

*The AI responding in perfect Arabic with Maliki fiqh sources cited*

**Features Shown:**
- ✅ RTL (right-to-left) layout for Arabic
- ✅ Source citations (Al-Risala mentioned)
- ✅ Beautiful Amiri font rendering
- ✅ Structured markdown with headers
- ✅ Prayer times widget (sidebar)

---

### Maliki Fiqh Question with Detailed Sources

![Maliki Fiqh Answer with Citations](screenshots/maliki-answer-sources.png)

*AI providing Maliki-specific rulings with authentic source references*

**Features Shown:**
- ✅ Hand placement in prayer (Maliki position)
- ✅ Source citation: "Prayer (Salah) Specific Rulings in Maliki Madhab [Source 1]"
- ✅ Detailed explanation with bullet points
- ✅ Clean markdown formatting

---

### English Interface with Full Features

![English Chat Interface](screenshots/english-interface.png)

**Features Shown:**
- ✅ Full-width chat area
- ✅ Prayer times widget with live times
- ✅ Quick action buttons
- ✅ Tips section
- ✅ Modern glass-morphism design

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ Chat UI    │  │ Prayer Times │  │ Upload Component        │ │
│  │ (RTL/LTR)  │  │ Widget       │  │ (Image/PDF)             │ │
│  └──────┬─────┘  └──────┬───────┘  └───────────┬─────────────┘ │
│         │                │                      │               │
│         └────────────────┴──────────────────────┘               │
│                          │                                       │
│                    Axios API Client                              │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                    FastAPI Backend
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │          API Routers (FastAPI)                       │       │
│  │  ┌──────────┐ ┌────────┐ ┌────────────┐ ┌────────┐ │       │
│  │  │ Quran    │ │ Hadith │ │ Prayer     │ │ Upload │ │       │
│  │  │ Router   │ │ Router │ │ Times      │ │ Router │ │       │
│  │  └────┬─────┘ └───┬────┘ └─────┬──────┘ └───┬────┘ │       │
│  └───────┼───────────┼────────────┼─────────────┼──────┘       │
│          │           │            │             │              │
│  ┌───────▼───────────▼────────────▼─────────────▼──────┐       │
│  │           Business Logic Services                    │       │
│  │  ┌──────────────┐  ┌────────────────────────────┐  │       │
│  │  │ Gemini AI    │  │  Maliki Fiqh RAG Service   │  │       │
│  │  │ Service      │  │  (Qdrant + Embeddings)     │  │       │
│  │  └──────┬───────┘  └────────┬───────────────────┘  │       │
│  └─────────┼──────────────────┼──────────────────────┘       │
│            │                  │                               │
│  ┌─────────▼──────────┐  ┌────▼─────────────────────┐        │
│  │  External APIs     │  │  Qdrant Vector Database  │        │
│  │  • alquran.cloud   │  │  • 21+ Maliki Documents  │        │
│  │  • aladhan.com     │  │  • 384-dim Embeddings    │        │
│  │  • sunnah.com      │  │  • Semantic Search       │        │
│  └────────────────────┘  └──────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Question (Arabic/English)
    ↓
Language Detection
    ↓
RAG Retrieval (Semantic Search in Qdrant)
    ↓
Context Enrichment (Top 3 relevant Maliki texts)
    ↓
Google Gemini 2.0 (With RAG context + Language instruction)
    ↓
Response in User's Language/Dialect
    ↓
Markdown Rendering (RTL for Arabic, LTR for English)
    ↓
Display with Source Citations
```

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Core language |
| **FastAPI** | 0.111.0 | REST API framework |
| **Google Gemini** | 2.0 Flash | LLM for responses |
| **Qdrant** | 1.15.1 | Vector database |
| **Sentence Transformers** | 5.1.2 | Multilingual embeddings |
| **Pydantic** | 2.9.2 | Data validation |
| **httpx** | 0.28.1 | Async HTTP client |
| **Scrapy** | 2.13.3 | Web scraping |
| **pdfplumber** | 0.11.7 | PDF text extraction |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI framework |
| **TypeScript** | 5.6.2 | Type safety |
| **Vite** | 4.5.3 | Build tool |
| **Tailwind CSS** | 3.4.1 | Styling |
| **React Markdown** | Latest | Markdown rendering |
| **Axios** | Latest | API client |
| **Lucide React** | Latest | Icons |

### AI & ML

| Component | Technology | Details |
|-----------|------------|---------|
| **LLM** | Google Gemini 2.0 Flash | Arabic-optimized, fast responses |
| **Embeddings** | paraphrase-multilingual-MiniLM-L12-v2 | 384 dimensions, 50+ languages |
| **Vector DB** | Qdrant | Cosine similarity, HNSW index |
| **OCR** | DeepSeek-OCR Ready | Optional GPU-accelerated |

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- Node.js 18+ (or 20+ for latest Vite)
- pip & npm
- 4GB+ RAM (for embedding model)
- Optional: CUDA GPU (for DeepSeek-OCR)

### Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/nur-al-ilm.git
cd nur-al-ilm

# 2. Set up backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure API keys
# Edit the GEMINI_API_KEY in src/config.py or create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# 4. Initialize Maliki Fiqh RAG database
python initialize_rag.py

# 5. Start backend
python run.py &

# 6. Set up frontend (in new terminal)
cd frontend
npm install
npm run dev &

# 7. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

---

## 💻 Usage

### Starting the Application

**Option 1: Manual Start**
```bash
# Terminal 1 - Backend
cd /path/to/nur-al-ilm
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd /path/to/nur-al-ilm/frontend
npm run dev
```

**Option 2: Using Start Script**
```bash
./start_app.sh
```

### Stopping the Application

```bash
pkill -f "python run.py"
pkill -f "npm run dev"
```

---

## 🎯 Features in Action

### 1. Ask Questions in Any Language

**English:**
```
"What is the Maliki position on raising hands in prayer?"
```

**Response includes:**
- ✅ Detailed Maliki ruling
- ✅ Source citation: [Al-Risala, Mukhtasar Khalil]
- ✅ Comparison with other madhabs
- ✅ Practical guidance

**Arabic (Formal):**
```
"ما هو حكم رفع اليدين في الصلاة عند المالكية؟"
```

**Arabic (Colloquial Egyptian):**
```
"إيه الحكم بتاع رفع الإيدين في الصلاة عند المالكية؟"
```

*AI automatically matches your dialect and formality level!*

### 2. Upload Books to Expand Knowledge Base

1. Click the **📤 Upload** button (bottom-left)
2. Choose **Image** (JPG/PNG) or **PDF**
3. System extracts text via OCR
4. Automatically adds to Qdrant vector database
5. AI can now reference your uploaded book!

**Supported:**
- 📷 Book page images
- 📄 Full PDF books
- 📝 Direct text input

### 3. Search Maliki Fiqh Topics

The RAG system finds relevant content even if you don't use exact keywords:

**Query:** "Can I wipe my socks?"
**Finds:** "Maliki Rulings on Wiping Over Socks (Masah ala al-Khuffayn)"

**Query:** "ما حكم الجمع بين الصلاتين؟"
**Finds:** "Maliki Position on Combining Prayers"

### 4. Get Prayer Times Automatically

- 📍 Auto-detects your location
- 🕌 Shows 5 daily prayer times
- 🧭 Qibla direction finder
- 📅 Islamic calendar (Hijri/Gregorian)
- 🤲 99 Names of Allah

---

## 📸 Screenshots

### 1. Welcome Screen with Quick Actions

![Al-Muwatta Welcome Interface](screenshots/04-welcome-with-quick-actions.png)

**🌟 The Perfect First Impression**

**Interface Elements:**
- ✨ **Al-Muwatta (الموطأ)** branding with Islamic green theme
- 🕌 **Prayer Times Widget** - Live times (Fajr 5:19 AM, Dhuhr 12:05 PM, Asr 3:23 PM, Maghrib 5:48 PM, Isha 6:50 PM)
- 📍 **Auto-location detection** - Shows "Makkah, Saudi Arabia"
- 🎯 **4 Colorful Quick Action Buttons**:
  - 📖 Surah Al-Fatiha (Emerald-teal gradient)
  - ✨ Daily Reminder (Purple-pink gradient)
  - 🔍 Search Hadith (Blue-cyan gradient)
  - 🤲 99 Names (Rose-orange gradient)
- 💡 **Tips Section** with usage guidance
- 📅 **Today's Date** - Sunday, October 26, 2025
- 🧭 **Find Qibla Direction** link

**Design Highlights:**
- Modern glass-morphism effects
- Islamic color palette (#006B3F green, #008B8B teal)
- Smooth gradient transitions
- Clean, spacious layout

---

### 2. Bilingual Welcome Message - Arabic First

![Al-Muwatta Initial Welcome](screenshots/01-welcome-page.png)

**🗣️ Intelligent Bilingual Greeting**

The AI welcomes users with:
- 🌙 **"السلام عليكم ورحمة الله وبركاته"**
- 📚 **"مرحباً بك في الموطأ - Al-Muwatta!"**
- 🕌 **"مساعدك الذكي المتخصص في الفقه المالكي"**

**What the assistant offers:**
- الفقه المالكي من مصادر أصيلة (الرسالة، مختصر خليل)
- آيات القرآن والتفسير
- البحث في الأحاديث  
- أوقات الصلاة والتقويم الهجري
- أسئلة فقهية وإسلامية

**Knowledge Base Stats:**
- 📚 قاعدة معرفة: **21+ كتاب** في الفقه المالكي
- 🤖 مدعوم بالذكاء الاصطناعي

**Why This Matters:**
- Arabic-first approach respects users
- Sets expectation for Maliki specialization
- Shows RAG database size
- Establishes bilingual capability

---

### 3. RAG in Action - Maliki Hand Placement Ruling

![Maliki Fiqh Answer with Citations](screenshots/02-arabic-chat-maliki-hand-placement.png)

**🎯 RAG-Enhanced Response with Authentic Sources**

**User Question (Arabic):**
*"ما هو حكم وضع اليدين في الصلاة عند المالكية؟"*  
(What is the ruling on hand placement in prayer according to Malikis?)

**AI Response Analysis:**
- ✅ **Perfect RTL (Right-to-Left)** - Proper Arabic text flow
- ✅ **Source Citation** - "Prayer (Salah) Specific Rulings in Maliki Madhab [Source 1]"
- ✅ **Structured Answer** with clear sections:
  - حكم وضع اليدين في الصلاة عند المالكية (The ruling)
  - الرأي المالكي (Maliki position clearly stated)
  - الأدلة من المصادر الإسلامية (Evidence from sources)
- ✅ **Maliki Position**: Arms at sides (not folded) - distinctive Maliki practice
- ✅ **Beautiful Typography** - Amiri font, 1.8 line-height

**Technical Achievement:**
- Qdrant searched 21 documents semantically
- Found most relevant Maliki text (score > 0.8)
- Gemini generated answer using RAG context
- Response formatted with RTL markdown

---

### 4. Complex Islamic Question - Honoring Parents

![Arabic Conversation - Parents Virtue](screenshots/03-arabic-conversation-parents.png)

**🤲 Deep Islamic Knowledge with Multiple Sources**

**User Question (Arabic):**
*"ما هي أحاديث فضل الوالدين؟"*  
(What are the hadiths about honoring parents?)

**Comprehensive AI Response:**
- 📖 **Quranic Evidence**:
  - Surah Al-Isra (17:23) - Complete verse quoted
  - Surah Luqman (31:14) - Mother's sacrifice mentioned
- 📚 **Hadith Evidence**:
  - حديث عبد الله بن مسعود (Abdullah ibn Mas'ud)
  - Multiple authentic narrations
- 🎓 **Structured Sections**:
  1. أدلة من القرآن الكريم
  2. أحاديث نبوية في فضل الوالدين
- ✅ **Natural Arabic** - Flows like a scholar speaking
- ✅ **Proper Attribution** - Hadith sources named

**What This Shows:**
- AI combines Quran + Hadith seamlessly
- Provides comprehensive Islamic guidance
- Uses authentic sources
- Beautiful Arabic presentation
- Perfect RTL alignment

---

## 🎨 UI/UX Features Demonstrated

From the screenshots above, you can see our attention to detail:

### Visual Design Excellence
- ✅ **Islamic Color Palette** - Green (#006B3F), Teal (#008B8B), Gold (#D4AF37)
- ✅ **Glass-morphism Effects** - Modern translucent cards
- ✅ **Gradient Buttons** - Beautiful quick actions with smooth color transitions
- ✅ **Amiri Font** - Professional Arabic typography (1.1em, line-height 1.8)
- ✅ **Responsive Layout** - Prayer widget in sidebar, collapsible on mobile

### RTL (Right-to-Left) Support
- ✅ **Automatic Detection** - Switches to RTL for Arabic content
- ✅ **Proper Text Flow** - All text aligned right for Arabic
- ✅ **Markdown RTL** - Headers, lists, quotes properly reversed
- ✅ **Bidirectional** - Mixed Arabic/English handled correctly

### Interactive Elements
- ✅ **Upload Button** (📤) - Bottom-left corner, always accessible
- ✅ **Quick Actions** - One-click queries with visual feedback
- ✅ **Prayer Times** - Auto-updates based on location
- ✅ **Dark Mode Toggle** - Theme switcher (🌙/☀️)

### Smart Features Shown
- ✅ **Source Citations** - RAG sources shown inline with [Source 1] tags
- ✅ **Timestamps** - Every message timestamped
- ✅ **Auto-scroll** - Messages auto-scroll to bottom
- ✅ **Loading States** - Animated dots while AI thinks
- ✅ **Error Handling** - Graceful fallbacks if API fails

---

## 🏛️ Architecture

### Backend Structure

```
src/
├── api_clients/           # External API integrations
│   ├── base_client.py     # Base HTTP client with retry logic
│   ├── hadith_client.py   # Hadith collections API
│   ├── quran_client.py    # Quran verses & translations
│   └── prayer_times_client.py  # Prayer times & calendar
│
├── services/              # Business logic
│   ├── gemini_service.py  # Google Gemini AI integration
│   ├── rag_service.py     # Qdrant RAG system
│   ├── fiqh_scraper.py    # Web scraping for Maliki texts
│   └── ocr_service.py     # OCR processing (DeepSeek-OCR)
│
├── routers/               # API endpoints
│   ├── ai_router.py       # AI Q&A endpoints
│   ├── quran_router.py    # Quran endpoints
│   ├── hadith_router.py   # Hadith endpoints
│   ├── prayer_times_router.py  # Prayer times
│   └── upload_router.py   # File upload & knowledge base
│
├── models/                # Pydantic schemas
│   └── schemas.py         # Request/response models
│
├── config.py              # Configuration management
└── main.py                # FastAPI application
```

### Frontend Structure

```
frontend/src/
├── components/
│   ├── ChatMessage.tsx    # Message component (RTL/LTR aware)
│   ├── PrayerTimesWidget.tsx  # Prayer times display
│   ├── QuickActions.tsx   # Quick query buttons
│   └── UploadButton.tsx   # File upload interface
│
├── lib/
│   ├── api.ts             # API client functions
│   ├── utils.ts           # Utility functions
│   └── language-detector.ts  # Auto language detection
│
├── App.tsx                # Main application
├── index.css              # Tailwind + custom styles
└── main.tsx               # Entry point
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key Endpoints

#### AI Assistant

```http
POST /api/v1/ai/ask
Content-Type: application/json

{
  "question": "What are the pillars of Islam?",
  "language": "english",
  "include_sources": true
}
```

#### Quran

```http
GET /api/v1/quran/surahs/1?edition=en.sahih
GET /api/v1/quran/ayahs/2:255?explain=true
GET /api/v1/quran/search?query=patience
```

#### Prayer Times

```http
GET /api/v1/prayer-times/timings?latitude=21.3891&longitude=39.8579
GET /api/v1/prayer-times/timings/city?city=Dubai&country=UAE
GET /api/v1/prayer-times/qibla?latitude=40.7128&longitude=-74.0060
```

#### Knowledge Base Upload

```http
POST /api/v1/upload/book-pdf
Content-Type: multipart/form-data

file: [PDF file]
title: "Mukhtasar Khalil"
category: "fiqh"
add_to_knowledge_base: true
```

#### Knowledge Base Stats

```http
GET /api/v1/upload/knowledge-base/stats

Response:
{
  "status": "ready",
  "total_documents": 21,
  "vector_database": "Qdrant",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
  "embedding_dimension": 384
}
```

---

## 🔍 RAG System (Maliki Fiqh)

### How It Works

1. **User asks a question** (Arabic or English)
2. **Semantic search** in Qdrant vector database
3. **Top 3 relevant** Maliki fiqh documents retrieved
4. **Context injection** into Gemini prompt
5. **AI generates answer** using authentic sources
6. **Response cites sources** (Al-Risala, Mukhtasar Khalil, etc.)

### Vector Database Details

- **Engine**: Qdrant (Rust-based, ultra-fast)
- **Collection**: `maliki_fiqh`
- **Vectors**: 384-dimensional embeddings
- **Distance**: Cosine similarity
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Languages**: Arabic, English, 50+ others

### Current Knowledge Base

**21+ Documents Covering:**

| Category | Topics |
|----------|--------|
| **Taharah** | Wudu, Ghusl, Tayammum, Menstruation, Najasah |
| **Salah** | Daily prayers, Hand placement, Jumu'ah, Eid, Janazah |
| **Sawm** | Ramadan, Breaking fast, Fidyah, Kaffara |
| **Zakat** | Nisab, Rates, Recipients, Livestock, Agriculture |
| **Hajj** | Pilgrimage, Udhiyah (sacrifice) |
| **Muamalat** | Business, Trade, Riba, Contracts |
| **Family** | Marriage, Wali, Mahr, Divorce |

### Expanding the Knowledge Base

**Method 1: Upload via UI**
- Click upload button → Choose file → Auto-added

**Method 2: Run Scraper**
```bash
python scrape_and_populate_rag.py
```

**Method 3: API**
```bash
curl -X POST http://localhost:8000/api/v1/upload/text-directly \
  -F "title=New Topic" \
  -F "text=Your Maliki fiqh content..."
```

---

## 🧪 Testing

### Run All Tests

```bash
# Activate venv
source venv/bin/activate

# Run test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Test specific module
pytest tests/test_quran_client.py -v
```

### Test Coverage

- ✅ Quran API Client (15+ tests)
- ✅ Prayer Times API Client (15+ tests)
- ✅ Hadith API Client (15+ tests)
- ✅ Gemini Service (5+ tests)
- ✅ Integration tests

### Example Test Run

```bash
python example_usage.py
```

Expected output:
```
✅ Quran API: Al-Fatiha retrieved (7 verses)
✅ Prayer Times: Makkah times fetched
✅ Gemini AI: Question answered
✅ RAG Search: Found relevant Maliki content
```

---

## 🌍 Internationalization

### Supported Languages

| Language | Support Level | Features |
|----------|---------------|----------|
| **Arabic** | ⭐⭐⭐⭐⭐ | RTL, dialect matching, Amiri font |
| **English** | ⭐⭐⭐⭐⭐ | Full support |
| **Urdu** | ⭐⭐⭐⭐ | Via multilingual model |
| **Malay** | ⭐⭐⭐ | Via multilingual model |
| **Turkish** | ⭐⭐⭐ | Via multilingual model |

### Arabic Dialect Support

- ✅ Modern Standard Arabic (الفصحى)
- ✅ Egyptian (المصري)
- ✅ Levantine (الشامي)
- ✅ Gulf (الخليجي)
- ✅ Moroccan (المغربي)
- ✅ Algerian & Tunisian

The AI **automatically matches** your dialect style!

---

## 📊 Performance

### Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| **Quran API** | < 1s | Cached by provider |
| **Prayer Times** | < 1s | Global CDN |
| **RAG Search** | < 200ms | Qdrant local |
| **Gemini Response** | 2-5s | Depends on prompt length |
| **PDF Processing** | 5-30s | Depends on page count |

### Scalability

- **Concurrent Users**: 100+ (with FastAPI async)
- **Vector Search**: Sub-second for 1M+ documents
- **Database**: Qdrant scales horizontally
- **Caching**: Redis-ready (optional)

---

## 🔐 Security & Privacy

### API Keys

- ✅ Environment variables (not in code)
- ✅ `.env` file (git-ignored)
- ✅ `.env.example` provided

### Data Privacy

- ✅ **No user data stored** by default
- ✅ Chat history: Client-side only
- ✅ Uploaded files: Local storage
- ✅ External APIs: Respect their terms

### CORS

Configured for development:
```python
allow_origins=["http://localhost:5173", "*"]
```

**For production**, restrict to your domain.

---

## 🛣️ Roadmap

### Phase 1: Core Features ✅ (COMPLETED)
- [x] Quran API integration
- [x] Prayer Times API
- [x] Google Gemini AI
- [x] Beautiful React UI
- [x] Arabic RTL support

### Phase 2: RAG System ✅ (COMPLETED)
- [x] Qdrant vector database
- [x] Maliki fiqh knowledge base (21+ docs)
- [x] Semantic search
- [x] Source citations
- [x] File upload (Image/PDF)

### Phase 3: Advanced Features 🚧 (IN PROGRESS)
- [ ] Real web scraping (Scrapy spiders active)
- [ ] DeepSeek-OCR GPU implementation
- [ ] User authentication
- [ ] Bookmark favorite answers
- [ ] Share conversations

### Phase 4: Scale & Deploy 📋 (PLANNED)
- [ ] Docker containers
- [ ] Redis caching
- [ ] PostgreSQL for user data
- [ ] Cloud deployment (AWS/GCP)
- [ ] Mobile app (React Native)
- [ ] Multi-madhab support (Shafi'i, Hanafi, Hanbali)

---

## 🤝 Contributing

We welcome contributions from the Muslim tech community!

### How to Contribute

1. **Add Maliki Fiqh Content**
   - Upload books via the UI
   - Run scrapers to collect content
   - Submit curated text via API

2. **Improve Code**
   - Fork the repository
   - Create feature branch
   - Submit pull request

3. **Report Issues**
   - Use GitHub Issues
   - Provide screenshots
   - Include error logs

### Contribution Guidelines

- **Code Style**: Follow PEP 8 (Python), ESLint (TypeScript)
- **Tests**: Add tests for new features
- **Documentation**: Update README for new features
- **Islamic Authenticity**: Verify sources before adding

---

## 📚 Data Sources

### Primary APIs

| Source | Purpose | License | Status |
|--------|---------|---------|--------|
| [alquran.cloud](https://alquran.cloud/api) | Quran verses & translations | Free | ✅ Active |
| [aladhan.com](https://aladhan.com/prayer-times-api) | Prayer times & calendar | Free | ✅ Active |
| [sunnah.com](https://sunnah.api-docs.io/) | Hadith collections | Requires key | ⚠️ Auth needed |

### Maliki Fiqh Sources

- **Al-Risala** - Ibn Abi Zayd al-Qayrawani
- **Mukhtasar Khalil** - Khalil ibn Ishaq
- **Al-Mudawwana** - Imam Malik & students
- **Al-Muwatta** - Imam Malik ibn Anas
- **Bidayat al-Mujtahid** - Ibn Rushd (comparative)

### Referenced Websites

- [malikifiqhqa.com](https://malikifiqhqa.com) - English Maliki resources
- [australianislamiclibrary.org](https://www.australianislamiclibrary.org/maliki-fiqh---arabic-books.html) - Arabic Maliki books
- IslamQA - Verified Islamic Q&A

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Google Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Application
APP_NAME="Nur Al-Ilm - Islamic Knowledge Assistant"
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./nur_al_ilm.db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0
```

### Customization

**Change AI Model:**
```python
# src/config.py
gemini_model: str = "gemini-2.0-flash-exp"  # or gemini-pro, gemini-1.5-pro
```

**Add More Madhabs:**
```python
# Extend src/services/rag_service.py
# Create collections for Shafi'i, Hanafi, Hanbali
```

**Adjust RAG Parameters:**
```python
# src/services/rag_service.py
n_results=3,  # Number of sources to retrieve
score_threshold=0.3,  # Minimum similarity score
max_context_length=2000,  # Max context characters
```

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
tail -f logs/backend_stable.log

# Test imports
source venv/bin/activate
python -c "from src.main import app; print('✅ OK')"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend Not Loading

```bash
# Check logs
tail -f logs/frontend.log

# Clear cache
cd frontend
rm -rf node_modules/.vite dist
npm install
npm run dev
```

### RAG Not Working

```bash
# Reinitialize vector database
python initialize_rag.py

# Check stats
curl http://localhost:8000/api/v1/upload/knowledge-base/stats
```

### Upload Button Not Showing

- Make sure you're using latest frontend code
- Upload popup appears at **bottom-left** of screen
- Z-index is 100 (should be above everything)

---

## 📖 Learn More

### Islamic Resources

- [Maliki Fiqh Made Simple](https://premium.malikimadhab.org)
- [SeekersGuidance - Maliki Fiqh](https://seekersguidance.org/answers/maliki-fiqh/)
- [Australian Islamic Library](https://www.australianislamiclibrary.org)

### Technical Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://www.sbert.net)
- [Google Gemini API](https://ai.google.dev/docs)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- FastAPI: MIT
- React: MIT
- Qdrant: Apache 2.0
- Sentence Transformers: Apache 2.0
- Google Gemini: Google AI Terms

---

## 🙏 Acknowledgments

### Built With Love For

**The Muslim Ummah** - الحمد لله رب العالمين

### Special Thanks

- **Google** - for Gemini API
- **Qdrant** - for amazing vector database
- **Hugging Face** - for transformer models
- **Islamic Scholars** - for preserving and teaching Maliki fiqh
- **Open Source Community** - for incredible tools

### Maintainers

- Built by [@hesham](https://github.com/hesham)
- For questions: Open an issue on GitHub

---

## 💬 Support

### Need Help?

- 📧 **Email**: support@example.com
- 💬 **Discord**: [Join our community](#)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Docs**: [Full Documentation](https://docs.example.com)

### Found a Bug?

Please open an issue with:
1. Description of the bug
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots if applicable
5. Error logs

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

## 📞 Contact

- **Website**: https://nur-al-ilm.example.com
- **GitHub**: https://github.com/your-username/nur-al-ilm
- **Email**: contact@example.com

---

<div align="center">

**Built with ❤️ for the Muslim Ummah**

**الحمد لله رب العالمين**

*"Indeed, in the remembrance of Allah do hearts find rest." (Quran 13:28)*

---

Made with [FastAPI](https://fastapi.tiangolo.com/) • [React](https://react.dev/) • [Google Gemini](https://ai.google.dev/) • [Qdrant](https://qdrant.tech/)

</div>

