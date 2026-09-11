# DeepShield (Kavach-AI)

AI-Powered Deepfake Search & Eradication Platform

## Overview

Automated digital safety platform that scans public web endpoints for unauthorized synthetic media (deepfakes), computes zero-biometric perceptual hashes, and automates Rule 3(1)(b) IT Rules legal takedowns & cybercrime dossiers.

## Core Principles

- **DPDP Act 2023 Compliant**: Zero persistent storage of biometric data
- **100% Free Stack**: Open-source libraries only
- **Human-in-the-Loop**: Explicit user confirmation for all legal actions

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 (App Router, TypeScript, Tailwind CSS)

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
deepshield/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   └── services/
│       ├── face_engine.py   # Face embedding & similarity
│       ├── hash_engine.py   # Perceptual hashing
│       ├── osint_search.py  # Web search module
│       ├── legal_email.py   # Legal notice sender
│       └── pdf_dossier.py   # Cybercrime dossier generator
└── frontend/
    ├── src/app/             # Next.js App Router pages
    ├── src/components/      # React components
    └── src/lib/             # API client & helpers
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/scan` | POST | Scan for deepfakes |
| `/api/legal-notice` | POST | Generate legal notice |
| `/api/matches` | GET | List detected matches |

## License

MIT
