# Quick Start Guide

## TL;DR - Get Running in 2 Minutes

```bash
# 1. Install backend
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn google-generativeai qdrant-client sentence-transformers httpx loguru python-dotenv pydantic-settings

# 2. Initialize RAG
python initialize_rag.py

# 3. Start backend
python run.py &

# 4. Install & start frontend
cd frontend && npm install && npm run dev &

# 5. Open browser
# http://localhost:5173
```

## Already Running?

**Frontend**: http://localhost:5173  
**Backend**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

## Test the RAG

Ask: **"What is the Maliki position on raising hands in prayer?"**

You'll see citations from Al-Risala and other Maliki sources!

## Upload a Book

1. Click 📤 button (bottom-left)
2. Choose image or PDF
3. Auto-added to knowledge base
4. Ask questions about it!

---

For detailed installation, see [INSTALLATION.md](INSTALLATION.md)

