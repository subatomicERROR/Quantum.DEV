#!/bin/bash
# File: ~/quantum.dev/stop-quantum.sh
# Purpose: Clean shutdown of Quantum.dev services (backend + frontend)

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛑 Stopping Quantum.dev processes on ports 8000 and 5500...${NC}"

for port in 8000 5500; do
    PID=$(lsof -ti tcp:$port)
    if [ -n "$PID" ]; then
        echo -e "🔨 Killing PID $PID on port $port"
        kill -9 $PID || true
    else
        echo -e "✅ No process found on port $port"
    fi
done

echo -e "${GREEN}✅ All services shut down successfully.${NC}"
