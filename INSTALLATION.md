# Installation Guide - Nur Al-Ilm

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Node.js 18+** (or 20+ recommended)
- **pip** (Python package manager)
- **npm** (Node package manager)
- **4GB+ RAM** (for embedding model)
- **Google Gemini API Key** (free at ai.google.dev)

Optional:
- **CUDA GPU** (for DeepSeek-OCR)
- **Redis** (for caching)

---

## Step-by-Step Installation

### 1. Clone or Download

```bash
cd /home/your-username
git clone https://github.com/your-repo/nur-al-ilm.git
cd nur-al-ilm
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

Create `.env` file in project root:

```bash
# Copy example
cp .env.example .env

# Edit with your API key
nano .env
```

Add your Gemini API key:
```
GEMINI_API_KEY=AIzaSyDfrRICbsvG94HYIFveimWgh9KQNvUpWYk
```

### 4. Initialize RAG Database

```bash
# This downloads the embedding model and creates vector database
python initialize_rag.py
```

Expected output:
```
✅ Embedding model loaded (384 dimensions)
✅ Knowledge base initialized with 5 documents
✅ RAG system ready
```

### 5. Add More Maliki Content

```bash
# Run scraper to add more documents
python scrape_and_populate_rag.py
```

This adds 13+ more documents (total: 21+)

### 6. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 7. Start Backend

In a new terminal:

```bash
# Activate venv
cd /path/to/nur-al-ilm
source venv/bin/activate

# Start server
python run.py
```

---

## Verification

### Check Backend

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "app_name": "Nur Al-Ilm - Islamic Knowledge Assistant",
  "version": "1.0.0"
}
```

### Check RAG

```bash
curl http://localhost:8000/api/v1/upload/knowledge-base/stats
```

Expected:
```json
{
  "total_documents": 21,
  "status": "ready",
  "vector_database": "Qdrant"
}
```

### Check Frontend

Open browser: http://localhost:5173

You should see:
- ✅ Chat interface
- ✅ Prayer times widget
- ✅ Upload button
- ✅ Quick action buttons

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/nur-al-ilm

# Activate venv
source venv/bin/activate

# Run from project root
python run.py
```

### Issue: Frontend shows "Failed to connect"

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in src/main.py
# Should include "http://localhost:5173"
```

### Issue: RAG returns no results

**Solution:**
```bash
# Reinitialize database
python initialize_rag.py

# Add more content
python scrape_and_populate_rag.py
```

### Issue: Vite version error

**Solution:**
```bash
cd frontend
npm install -D vite@4.5.3 @vitejs/plugin-react@4.2.1
```

---

## Production Deployment

### Backend (FastAPI)

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)

```bash
cd frontend

# Build for production
npm run build

# Serve with nginx or serve
npx serve -s dist -l 3000
```

### Docker (Coming Soon)

```bash
docker-compose up -d
```

---

## Next Steps

1. **Open**: http://localhost:5173
2. **Try asking**: "What is the Maliki position on prayer?"
3. **Upload a book**: Click upload button, add Maliki fiqh PDF
4. **Explore API**: http://localhost:8000/docs

Happy learning! الحمد لله 🌟

