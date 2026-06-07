#!/bin/bash

# Local Development Startup Script
# Starts both frontend and backend servers for local testing

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/phase5/backend"
FRONTEND_DIR="$PROJECT_ROOT/phase5/frontend"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         TodoGenie - Local Development Environment Setup         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ Node.js/npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js/npm found${NC}"

echo ""
echo "📦 Setting up Backend..."

# Backend setup
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv_local" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv_local
fi

# Activate virtual environment
source venv_local/bin/activate

# Install dependencies
if [ ! -f "venv_local/pyvenv.cfg" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Backend setup failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend environment ready${NC}"

echo ""
echo "🎨 Setting up Frontend..."

# Frontend setup
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --legacy-peer-deps
fi

echo -e "${GREEN}✓ Frontend environment ready${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Ready to Start Development!                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Instructions:"
echo ""
echo "1️⃣  BACKEND (Terminal 1):"
echo "   cd $BACKEND_DIR"
echo "   source venv_local/bin/activate"
echo "   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "2️⃣  FRONTEND (Terminal 2):"
echo "   cd $FRONTEND_DIR"
echo "   npm run dev"
echo ""
echo "3️⃣  ACCESS:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "📚 For more details, see: LOCAL_DEVELOPMENT.md"
echo ""
