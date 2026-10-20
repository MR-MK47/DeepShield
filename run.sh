#!/usr/bin/env bash
# DeepShield - One-Click Launcher & Setup for macOS & Linux
set -e

echo "========================================================"
echo "       DeepShield - One-Click Launcher & Setup"
echo "========================================================"
echo ""

# Determine python command
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed or not in PATH."
    echo "Please install Python 3.10+ (https://www.python.org/)."
    exit 1
fi

# Check Node.js and npm
if ! command -v npm &>/dev/null; then
    echo "[ERROR] Node.js and npm are not installed or not in PATH."
    echo "Please install Node.js 18+ LTS (https://nodejs.org/)."
    exit 1
fi

# 1. Environment files
if [ ! -f "backend/.env" ]; then
    echo "[INFO] Creating backend/.env from template..."
    cp backend/.env.example backend/.env
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "[INFO] Creating frontend/.env.local from template..."
    cp frontend/.env.example frontend/.env.local
fi

# 2. Virtual environment setup
if [ ! -d "backend/venv" ]; then
    echo "[INFO] Creating Python virtual environment in backend/venv..."
    $PYTHON_CMD -m venv backend/venv
    source backend/venv/bin/activate
    pip install --upgrade pip
    echo "[INFO] Installing backend dependencies..."
    if ! pip install -r backend/requirements.txt; then
        echo ""
        echo "[WARNING] Full requirements failed (e.g. C++ build tools missing for InsightFace)."
        echo "[INFO] Installing core lightweight dependencies (pHash fallback mode)..."
        pip install -r backend/requirements-core.txt
    fi
    deactivate
fi

# 3. Frontend node_modules setup
if [ ! -d "frontend/node_modules" ]; then
    echo "[INFO] Installing frontend npm packages..."
    (cd frontend && npm install)
fi

echo ""
echo "========================================================"
echo "[OK] All dependencies and environments are ready!"
echo "Starting DeepShield Backend and Frontend..."
echo "========================================================"
echo ""
echo "- Frontend Dashboard: http://localhost:3000"
echo "- Backend API Docs:   http://localhost:8000/docs"
echo "Press Ctrl+C to stop all servers."
echo ""

# Start backend and frontend in background and manage exit
source backend/venv/bin/activate
(cd backend && uvicorn main:app --reload --port 8000) &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Stopping DeepShield servers..."
    kill "$BACKEND_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
    echo "Servers stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT
wait
