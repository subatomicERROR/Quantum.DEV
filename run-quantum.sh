#!/bin/bash
# File: ~/quantum.dev/run-quantum.sh
# Purpose: Unified runner for Quantum.dev system (backend + frontend)

set -e  # Stop script on any error

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Check .env exists
if [ ! -f .env ]; then
    echo -e "${GREEN}⚠️  .env not found. Create one before running secure models.${NC}"
else
    echo -e "${GREEN}✅ .env found, secure tokens can be loaded.${NC}"
fi

# Run backend (FastAPI)
echo -e "${GREEN}🚀 Starting FastAPI backend on http://127.0.0.1:8000 ...${NC}"
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Always serve frontend
echo -e "${GREEN}🖥️  Serving frontend at http://127.0.0.1:5500 ...${NC}"
cd frontend
python3 -m http.server 5500 &
FRONTEND_PID=$!
xdg-open http://127.0.0.1:5500 &
cd ..

# Optional future enhancements (Quantum test hook, agent start, etc.)
# echo "🧪 Running quantum tests..."
# python tests/test_quantum_core.py

# Wait until user terminates
echo -e "${GREEN}✅ Quantum.dev system is now running.${NC}"
echo "📦 Backend running on: http://127.0.0.1:8000"
echo "📄 Docs available at: http://127.0.0.1:8000/docs"
echo "🌐 Frontend served at: http://127.0.0.1:5500"

echo -e "\n🛑 Press [CTRL+C] to stop everything."

# Keep script alive
wait $BACKEND_PID
wait $FRONTEND_PID
