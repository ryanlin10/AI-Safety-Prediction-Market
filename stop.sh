#!/bin/bash
# Stop script for AI Safety Prediction Market
# Stops both frontend and backend services

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Safety Prediction Market - Stopping Services         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop backend
echo "Stopping Backend (port 5001)..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    kill $(lsof -t -i:5001) 2>/dev/null || true
    echo "${GREEN}  ✓ Backend stopped${NC}"
else
    echo "  Backend not running"
fi

# Stop frontend  
echo "Stopping Frontend (port 3000)..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    kill $(lsof -t -i:3000) 2>/dev/null || true
    echo "${GREEN}  ✓ Frontend stopped${NC}"
else
    echo "  Frontend not running"
fi

# Kill any remaining Python processes running run_local.py
pkill -f "python.*run_local.py" 2>/dev/null || true

# Kill any remaining npm processes
pkill -f "npm start" 2>/dev/null || true

echo ""
echo "${GREEN}All services stopped${NC}"
echo ""

