# Windows Setup Guide for DeepShield

This step-by-step guide explains how to set up and run **DeepShield** on a fresh Windows machine with no pre-installed developer tools.

---

## 1. Prerequisites Installation

### Step A: Install Git
1. Download Git for Windows: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Run the installer and keep the default options.

### Step B: Install Python 3.11
1. Download Python 3.11 installer: [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)
2. **IMPORTANT CRITICAL STEP**: On the first setup screen, check the box:
   `[X] Add python.exe to PATH` before clicking **Install Now**.

### Step C: Install Node.js LTS
1. Download Node.js LTS installer: [https://nodejs.org/](https://nodejs.org/)
2. Run the installer with default settings.

---

## 2. Clone the Repository

Open **PowerShell** or **Command Prompt** (CMD) and run:

```powershell
git clone https://github.com/MR-MK47/DeepShield.git
cd DeepShield
```

---

## 3. Backend Setup (FastAPI & AI Engine)

In your terminal, navigate to the `backend` directory and set up the Python virtual environment:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> **Note**: On initial startup, InsightFace will automatically download lightweight model weights. Heavy model files (`.onnx`, `.zip`) are stored in `.insightface/` and excluded from Git tracking.

To start the FastAPI backend server on port 8000:

```powershell
uvicorn main:app --reload --port 8000
```

---

## 4. Frontend Setup (Next.js 14)

Open a **second** PowerShell or CMD terminal window and run:

```powershell
cd DeepShield/frontend
npm install
npm run dev
```

The Next.js dashboard will start at: `http://localhost:3000`

---

## 5. Summary of Server Endpoints

- **Frontend Dashboard**: `http://localhost:3000`
- **Scan Console**: `http://localhost:3000/scan`
- **FastAPI Backend**: `http://localhost:8000`
- **API Health Check**: `http://localhost:8000/api/health`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
