# API Reference - Nur Al-Ilm

Complete reference for all API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. All endpoints are open.

---

## AI Assistant Endpoints

### Ask Islamic Question

```http
POST /api/v1/ai/ask
```

**Request Body:**
```json
{
  "question": "What are the pillars of Islam?",
  "language": "english",
  "include_sources": true
}
```

**Response:**
```json
{
  "content": "The five pillars of Islam are...",
  "language": "english",
  "model": "gemini-2.0-flash-exp",
  "metadata": {
    "question": "What are the pillars of Islam?",
    "include_sources": true
  }
}
```

---

### Get Daily Reminder

```http
GET /api/v1/ai/daily-reminder?theme=gratitude&language=english
```

**Response:**
```json
{
  "content": "**Daily Reminder: Gratitude**\n\n...",
  "language": "english",
  "model": "gemini-2.0-flash-exp"
}
```

---

### Translate Islamic Text

```http
POST /api/v1/ai/translate
```

**Request:**
```json
{
  "text": "الحمد لله",
  "source_lang": "arabic",
  "target_lang": "english"
}
```

---

## Quran Endpoints

### Get Surah

```http
GET /api/v1/quran/surahs/{surah_number}?edition=en.sahih&explain=false
```

**Parameters:**
- `surah_number` (1-114)
- `edition` (optional): quran-uthmani, en.sahih, etc.
- `explain` (boolean): Get AI tafsir

**Example:**
```bash
curl http://localhost:8000/api/v1/quran/surahs/1?edition=en.sahih
```

---

### Search Quran

```http
GET /api/v1/quran/search?query=patience&surah=2
```

---

## Prayer Times Endpoints

### Get Prayer Times by Coordinates

```http
GET /api/v1/prayer-times/timings?latitude=21.3891&longitude=39.8579&method=2
```

**Calculation Methods:**
- 1: University of Islamic Sciences, Karachi
- 2: Islamic Society of North America (ISNA)
- 3: Muslim World League (MWL)
- 4: Umm al-Qura, Makkah
- ...13 total methods

---

### Get Prayer Times by City

```http
GET /api/v1/prayer-times/timings/city?city=Dubai&country=UAE
```

---

### Get Qibla Direction

```http
GET /api/v1/prayer-times/qibla?latitude=40.7128&longitude=-74.0060
```

---

## Knowledge Base & Upload Endpoints

### Upload Book Image (OCR)

```http
POST /api/v1/upload/book-image
Content-Type: multipart/form-data

file: [image file]
title: "Mukhtasar Khalil - Page 15"
category: "salah"
add_to_knowledge_base: true
```

---

### Upload PDF Book

```http
POST /api/v1/upload/book-pdf
Content-Type: multipart/form-data

file: [PDF file]
title: "Al-Risala"
category: "general"
max_pages: 50
add_to_knowledge_base: true
```

---

### Add Text Directly

```http
POST /api/v1/upload/text-directly
Content-Type: application/x-www-form-urlencoded

title=New Maliki Ruling
text=Your fiqh content here...
category=fiqh
source=Mukhtasar Khalil
```

---

### Get Knowledge Base Statistics

```http
GET /api/v1/upload/knowledge-base/stats
```

**Response:**
```json
{
  "status": "ready",
  "total_documents": 21,
  "collection_name": "maliki_fiqh",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
  "embedding_dimension": 384,
  "vector_database": "Qdrant"
}
```

---

### Search Knowledge Base Directly

```http
POST /api/v1/upload/knowledge-base/search
Content-Type: application/x-www-form-urlencoded

query=prayer rulings
n_results=5
category=salah
```

**Response:**
```json
{
  "status": "success",
  "query": "prayer rulings",
  "results_count": 3,
  "results": [
    {
      "text": "# Prayer in Maliki Fiqh...",
      "metadata": {
        "topic": "Prayer (Salah) Specific Rulings",
        "category": "salah",
        "source": "Maliki Fiqh Compilation"
      },
      "score": 0.87
    }
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error
- `503` - Service Unavailable

---

## Rate Limiting

Currently no rate limiting. For production, consider:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Examples

### Python

```python
import httpx
import asyncio

async def ask_question():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/ai/ask",
            json={
                "question": "What is Tawheed?",
                "language": "english"
            }
        )
        return response.json()

result = asyncio.run(ask_question())
print(result['content'])
```

### JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:8000/api/v1/ai/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What are the pillars of Islam?',
    language: 'english',
  }),
});

const data = await response.json();
console.log(data.content);
```

### cURL

```bash
# Ask question
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Zakat?", "language": "english"}'

# Get Surah
curl http://localhost:8000/api/v1/quran/surahs/1?edition=en.sahih

# Upload text
curl -X POST http://localhost:8000/api/v1/upload/text-directly \
  -F "title=New Ruling" \
  -F "text=Content here..."
```

---

For full interactive documentation, visit: **http://localhost:8000/docs**

