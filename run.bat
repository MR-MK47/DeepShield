@echo off
echo Starting DeepShield...

:: Start the FastAPI backend in a new window
echo Starting Backend...
start "DeepShield Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start the Next.js frontend in a new window
echo Starting Frontend...
start "DeepShield Frontend" cmd /k "cd frontend && npm run dev"

echo DeepShield servers are booting up in separate windows!
echo Frontend will be available at: http://localhost:3000
echo Backend API will be available at: http://localhost:8000