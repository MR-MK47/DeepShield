# DeepShield (Kavach-AI)

DeepShield is a prototype for discovering **candidate images** that may resemble a supplied reference image, inspecting source URLs, and preparing operator-reviewed evidence reports or takedown-request emails.

It is not a deepfake classifier, legal adviser, or guarantee of takedown. Similarity does not establish that content is synthetic, unlawful, or an impersonation.

## Current capabilities

- Next.js 14 dashboard with image upload, keyword-assisted public image search, candidate results, selection and evidence copying.
- FastAPI image analysis using InsightFace ArcFace when its model is available. If unavailable or no face is detected, the engine uses a clearly typed perceptual-hash fallback; it does not compare face embeddings to perceptual hashes.
- Perceptual hashing using standard pHash. Genuine PDQ hashing is used only when the optional pdqhash native binding is installed; installation may require platform-specific build support.
- Public image discovery using DDGS, bounded remote image downloads, URL safety checks and similarity candidate filtering.
- Local operator registration and login, password hashing, expiring server-side sessions and authenticated legal/report endpoints.
- Explicit review before legal-notice submission, a safe local no-send test mode, actual Resend provider submission when deliberately enabled, and PDF candidate-evidence reports.
- No intentional application-level persistence of reference image uploads or extracted vector data. Verify the complete hosting/runtime stack before making formal privacy-compliance claims.

## Requirements

- Python 3.11 recommended.
- Node.js 18.17+ (Node 20 LTS recommended) and npm.
- Network access is needed for public image search. Real ArcFace analysis may download InsightFace model files on first use; without a usable model, the API can fall back to pHash.
- The default NOTICE_EMAIL_MODE=mock exercises the preview/confirmation flow without sending email. Preview requires authentication; actual sending can only consume a short-lived preview created by the same operator. Live sending requires NOTICE_EMAIL_MODE=resend, a valid Resend API key, a verified sender, and explicitly configured, independently verified platform recipient addresses. A provider acceptance does not guarantee platform action.

## Setup on Windows

Open PowerShell or Command Prompt from the repository folder.

### Backend

~~~powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
~~~

If you already have a local .env, keep it; do not overwrite it. Add new settings from .env.example only when missing. For ordinary local testing, keep NOTICE_EMAIL_MODE=mock: you can exercise the full notice preview/confirmation workflow, and the interface will clearly say that no email was sent. To enable a real external email, deliberately set NOTICE_EMAIL_MODE=resend and configure RESEND_API_KEY, RESEND_FROM_EMAIL, CORS_ORIGINS, plus the relevant verified platform contact (META_GRIEVANCE_EMAIL, GOOGLE_ABUSE_EMAIL, X_ABUSE_EMAIL or TIKTOK_LEGAL_EMAIL). Missing/unverified contacts block live delivery. Never commit your real .env.

For a quick offline-safe smoke test without downloading a face model, set DEEPSHIELD_DISABLE_FACE_MODEL=1 in the terminal before starting the backend. This uses pHash fallback and is **not** a test of ArcFace accuracy.

### Frontend

Open a second terminal in the repository folder.

~~~powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
~~~

Open http://localhost:3000. The API URL defaults to http://localhost:8000.

### Start both using the helper

After creating backend/venv, installing backend requirements, and running npm install under frontend, execute run.bat from the repository root.

## Setup on macOS/Linux

Backend:

~~~bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
~~~

Frontend (in a second terminal):

~~~bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
~~~

## Tests

Run backend tests without a model download or outbound image-search calls.

Windows PowerShell:

~~~powershell
cd backend
.\venv\Scripts\activate
$env:DEEPSHIELD_DISABLE_FACE_MODEL="1"
python -m pytest -q
~~~

macOS/Linux:

~~~bash
cd backend
DEEPSHIELD_DISABLE_FACE_MODEL=1 python -m pytest -q
~~~

Frontend checks:

~~~bash
cd frontend
npm ci
npm test
npm run lint
npm run build
~~~

The default local test mode never sends real emails. Automated tests also mock the provider and do not send external messages. Search accuracy and ArcFace identity-matching performance require a separate labelled real-image evaluation; passing the unit suite does not prove those metrics.

## API endpoints

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| GET | `/` | Health check | No |
| GET | `/api/health` | Health check | No |
| POST | `/api/auth/register` | Create operator account | No |
| POST | `/api/auth/login` | Sign in and receive session token | No |
| GET | `/api/auth/me` | Get current operator | Bearer token |
| POST | `/api/auth/logout` | Revoke session | Bearer token optional |
| POST | `/api/analyze` | Validate image and generate vector/signature | No |
| POST | `/api/search` | Search candidates; optional opt-in history save | No (Bearer token required to save) |
| POST | `/api/scan` | Combined image analysis and candidate search | No (Bearer token required to save history) |
| GET | `/api/matches` | List the operator's explicitly saved scans | Bearer token |
| DELETE | `/api/matches/{scan_id}` | Delete a saved scan | Bearer token |
| POST | `/api/dossier` | Generate candidate-evidence PDF | Bearer token |
| POST | `/api/takedown/preview` | Prepare preview without sending email | Bearer token |
| POST | `/api/legal-notice` | Alias for the no-send notice preview | Bearer token |
| POST | `/api/takedown/email` | Submit a reviewed preview in test mode or via Resend | Bearer token |

## Important configuration and scope

Backend environment settings are documented in backend/.env.example; frontend settings are documented in frontend/.env.example. Local operator accounts are stored in a SQLite file ignored by Git, and session token hashes—not raw tokens—are stored in the database.

Configure CORS_ORIGINS to exactly match the frontend origins you use. Configure platform contact variables only after independently verifying the intended recipients. Do not treat old prototype recipient addresses as verified current grievance contacts.

The login/session features do not currently include email-based password recovery, multi-factor authentication, a hosted user-management console, or role administration. Saved scan history is optional and off by default. When an operator explicitly checks “Save these results to my account history,” only candidate URLs, domains, scores, signatures, query text and timestamps are saved under that account; uploaded reference images and face vectors are not included. History is visible at /history and can be deleted per scan.

The app uses search-provider results and remote image URLs that can be blocked, expired, rate-limited or irrelevant. This prototype does not independently classify synthetic media. Operator review is required before sending any notice or relying on a generated evidence report.

## Repository structure

~~~text
backend/
  main.py
  services/
    auth.py
    face_engine.py
    hash_engine.py
    osint_search.py
    legal_email.py
    pdf_dossier.py
  test_*.py
frontend/
  src/app/
  src/components/
  src/lib/api.ts
~~~

## License

MIT
