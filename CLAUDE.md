# CLAUDE.md - AI Coding Instructions for DeepShield

## Project Overview
**Name**: DeepShield (AI-Powered Deepfake Search & Eradication Platform)
**Purpose**: An automated digital safety platform that scans public web endpoints for unauthorized synthetic media (deepfakes), computes zero-biometric perceptual hashes, and automates Rule 3(1)(b) IT Rules legal takedowns & cybercrime dossiers.

## Core Technical Constraints & Non-Negotiables
1. **DPDP Act 2023 Compliance**: Absolute zero persistent storage of biometric face vectors or reference images. Process photos in memory and purge immediately after vectorization.
2. **100% Free Stack**: Use open-source libraries (`insightface`/`face_recognition`, `pdqhash`/`imagehash`, `duckduckgo_search`, `reportlab`, `resend`) to ensure zero operational cost.
3. **Human-in-the-Loop**: Every legal notice dispatch or dossier generation MUST require explicit user confirmation on the UI.

## Repository Structure
```
├── backend/                  # Python FastAPI Backend
│   ├── main.py               # FastAPI entry point & routes
│   ├── requirements.txt      # Dependencies
│   └── services/
│       ├── face_engine.py    # Face embedding & cosine similarity
│       ├── hash_engine.py    # PDQ & pHash perceptual hashing
│       ├── osint_search.py   # Web search & candidate filtering
│       ├── legal_email.py    # Resend SMTP legal notice sender
│       └── pdf_dossier.py    # ReportLab Cybercrime Dossier builder
└── frontend/                 # Next.js 14 Dashboard
    ├── app/                  # App Router pages & layout
    ├── components/           # UI components (Upload, Matches, Actions)
    └── lib/                  # API client & helpers
```

## Setup & Run Commands

### Backend (Python FastAPI)
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate | On Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev # Runs at http://localhost:3000
```

## Code Style & Rules
- **Backend**: Use Python 3.11+, type hints, `pydantic` models for request/response bodies, async handlers where applicable.
- **Frontend**: Next.js App Router (TypeScript), Tailwind CSS, Lucide icons, clean card-based UI.
- **API Protocol**: Restful JSON endpoints. Return clean error responses with proper HTTP status codes.
