@echo off
setlocal

REM Ensure current working directory is the folder containing run.bat
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo ========================================================
echo        DeepShield - One-Click Launcher and Setup
echo ========================================================
echo.

REM 1. Detect Python command
set "PYCMD="
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYCMD=python"
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYCMD=py"
    )
)

if "%PYCMD%"=="" (
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python 3.10 or 3.11 from https://www.python.org/
    echo Make sure to check Add Python to PATH during installation.
    pause
    exit /b 1
)

REM 2. Check Node.js and npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js or npm is not found in your PATH!
    echo Please install Node.js 18 or 20 LTS from https://nodejs.org/
    pause
    exit /b 1
)

REM 3. Setup backend environment file
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from template...
    copy "backend\.env.example" "backend\.env" >nul
)

REM 4. Setup frontend environment file
if not exist "frontend\.env.local" (
    echo [INFO] Creating frontend\.env.local from template...
    copy "frontend\.env.example" "frontend\.env.local" >nul
)

REM 5. Setup Python virtual environment if missing or incomplete
if not exist "backend\venv\Scripts\uvicorn.exe" (
    echo [INFO] Virtual environment or packages missing. Preparing backend\venv...
    if exist "backend\venv" (
        echo [INFO] Cleaning up incomplete venv...
        rmdir /s /q "backend\venv"
    )
    echo [INFO] Creating Python virtual environment in backend\venv...
    %PYCMD% -m venv backend\venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create Python virtual environment.
        echo Please ensure Python 3.10+ is properly installed.
        pause
        exit /b 1
    )
    echo [INFO] Installing backend dependencies...
    "backend\venv\Scripts\python.exe" -m pip install --upgrade pip
    "backend\venv\Scripts\pip.exe" install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] Full requirements failed - InsightFace C++ build tools missing.
        echo [INFO] Installing core lightweight dependencies - pHash fallback mode...
        "backend\venv\Scripts\pip.exe" install -r backend\requirements-core.txt
    )
)

REM 6. Setup Frontend dependencies if missing
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend npm packages - this may take a minute...
    cd /d "%ROOT_DIR%frontend"
    call npm install
    cd /d "%ROOT_DIR%"
)

echo.
echo ========================================================
echo [OK] All dependencies and environments are ready!
echo Starting DeepShield Backend - FastAPI and Frontend - Next.js...
echo ========================================================
echo.

REM Start the FastAPI backend in a new window using python -m uvicorn
start "DeepShield Backend" cmd /k "cd /d "%ROOT_DIR%backend" && "%ROOT_DIR%backend\venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000"

REM Start the Next.js frontend in a new window
start "DeepShield Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

echo DeepShield is booting up!
echo - Frontend Dashboard: http://localhost:3000
echo - Backend API Docs:   http://localhost:8000/docs
echo.
pause