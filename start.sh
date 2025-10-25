#!/bin/bash
# Start script for AI Safety Prediction Market
# Runs both frontend and backend in the background

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Safety Prediction Market - Starting Services         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if services are already running
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "${YELLOW}Backend already running on port 5001${NC}"
else
    echo "${BLUE}Starting Backend...${NC}"
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate
    nohup python run_local.py > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "  Backend PID: $BACKEND_PID"
    sleep 3
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "${GREEN}  ✓ Backend started successfully${NC}"
    else
        echo "${YELLOW}  ⚠ Backend may have failed to start. Check backend.log${NC}"
    fi
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "${YELLOW}Frontend already running on port 3000${NC}"
else
    echo "${BLUE}Starting Frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"
    nohup npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "  Frontend PID: $FRONTEND_PID"
    sleep 5
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "${GREEN}  ✓ Frontend started successfully${NC}"
    else
        echo "${YELLOW}  ⚠ Frontend may have failed to start. Check frontend.log${NC}"
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Services Running! 🚀                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo "  Backend:   ${GREEN}http://localhost:5001${NC}"
echo "  API:       ${GREEN}http://localhost:5001/api${NC}"
echo ""
echo "  Logs:"
echo "  - Backend:  tail -f backend/backend.log"
echo "  - Frontend: tail -f frontend/frontend.log"
echo ""
echo "To stop services: ./stop.sh"
echo ""


