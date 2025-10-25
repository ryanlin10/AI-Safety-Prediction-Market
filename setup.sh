#!/bin/bash
# Setup script for AI Safety Prediction Market
# Sets up both frontend and backend development environments

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Safety Prediction Market - Setup Script              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Backend Setup
echo "${YELLOW}[1/3] Setting up Backend (Python)...${NC}"
cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo "  → Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "  → Virtual environment already exists"
fi

echo "  → Activating virtual environment..."
source venv/bin/activate

echo "  → Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "${GREEN}  ✓ Backend setup complete${NC}"
echo ""

# Frontend Setup
echo "${YELLOW}[2/3] Setting up Frontend (Node.js)...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "  → Installing Node.js dependencies..."
    npm install
else
    echo "  → Node modules already installed, updating..."
    npm install
fi

echo "${GREEN}  ✓ Frontend setup complete${NC}"
echo ""

# Database Setup
echo "${YELLOW}[3/3] Setting up Database...${NC}"
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

echo "  → Running database seed script..."
python seed_data.py

echo "${GREEN}  ✓ Database setup complete${NC}"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Setup Complete! 🎉                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && source venv/bin/activate && python run_local.py"
echo "  2. Frontend: cd frontend && npm start"
echo ""
echo "Or use the start.sh script: ./start.sh"
echo ""

