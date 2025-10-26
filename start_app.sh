#!/bin/bash

# Nur Al-Ilm - Start Both Frontend and Backend
# This script starts both the FastAPI backend and React frontend

echo "🌟 Starting Nur Al-Ilm - نور العلم"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill existing processes on ports 8000 and 5173
echo "${YELLOW}🔍 Checking for existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start Backend
echo ""
echo "${BLUE}🚀 Starting FastAPI Backend on http://localhost:8000${NC}"
cd "$(dirname "$0")"
source venv/bin/activate
python run.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 3

# Start Frontend
echo ""
echo "${GREEN}🎨 Starting React Frontend on http://localhost:5173${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait a bit for frontend to start
sleep 3

echo ""
echo "${GREEN}✨ Nur Al-Ilm is ready!${NC}"
echo "=================================="
echo ""
echo "📖 Frontend: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    echo "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Keep script running
echo "Logs are being written to:"
echo "  - Backend: logs/backend.log"
echo "  - Frontend: logs/frontend.log"
echo ""

# Follow both logs
tail -f logs/backend.log logs/frontend.log

