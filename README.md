# DeepShield (Kavach-AI)

DeepShield is a prototype for discovering **candidate images** that may resemble a supplied reference image, inspecting source URLs, and preparing operator-reviewed evidence reports or takedown-request emails.

It is not a deepfake classifier, legal adviser, or guarantee of takedown. Similarity does not establish that content is synthetic, unlawful, or an impersonation.

## Current capabilities

- Next.js 14 dashboard with image upload, keyword-assisted public image search, candidate results, selection and evidence copying.
- FastAPI image analysis using InsightFace ArcFace when its model is available. If unavailable or no face is detected, the engine uses a clearly typed perceptual-hash fallback; it does not compare face embeddings to perceptual hashes.
- Perceptual hashing using standard pHash. Genuine PDQ hashing is used only when the optional pdqhash native binding is installed; installation may require platform-specific build support.
- Public image discovery using DDGS, bounded remote image downloads, URL safety checks and similarity candidate filtering.
- Local operator registration and login, password hashing, expiring server-side sessions and authenticated legal/report endpoints.
- A review modal rendered above the result grid, website-specific contact discovery from public homepage/contact/privacy/legal pages, an editable email recipient, a no-send local test mode, Resend submission after explicit confirmation, and PDF candidate-evidence reports.
- No intentional application-level persistence of reference image uploads or extracted vector data. Verify the complete hosting/runtime stack before making formal privacy-compliance claims.

## Requirements

- Python 3.11 recommended.
- Node.js 18.17+ (Node 20 LTS recommended) and npm.
- Network access is needed for public image search. Real ArcFace analysis may download InsightFace model files on first use; without a usable model, the API can fall back to pHash.
- NOTICE_EMAIL_MODE=auto uses Resend when RESEND_API_KEY is configured and safely falls back to local no-send mode when the key is absent. Use NOTICE_EMAIL_MODE=mock to force no-send testing or resend to require live delivery. The app searches public contact pages on the matched website and displays source links; operators can edit the address manually. Preview and dispatch require authentication, and dispatch consumes a short-lived preview created by the same operator. Live delivery also requires a sender address on a domain verified in Resend. Provider acceptance is not proof of delivery or removal.

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

If you already have a local .env, keep it; do not overwrite it. Since an existing .env is not updated by git pull, change its NOTICE_EMAIL_MODE setting from the old mock default to auto (or resend) to enable Resend with your existing RESEND_API_KEY. With auto, a configured key selects Resend; if no key is configured, the app stays in no-send test mode. To force local testing, set NOTICE_EMAIL_MODE=mock. Set RESEND_FROM_EMAIL to an address on a domain verified in your Resend account; the sample onboarding@resend.dev sender is for Resend testing and is blocked for sending notices to arbitrary external website contacts. After you review and confirm a notice, the backend sends it to Resend using the recipient displayed in the preview. Contact discovery only suggests public email addresses; verify the correct department and recipient before sending. Never commit your real .env.

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

Automated tests always mock the Resend provider and never send external messages. To force no-send behavior locally even when an API key is configured, set NOTICE_EMAIL_MODE=mock. With NOTICE_EMAIL_MODE=auto, a configured RESEND_API_KEY selects Resend, and a missing key falls back to no-send test mode. Search accuracy and ArcFace identity-matching performance require a separate labelled real-image evaluation; passing the unit suite does not prove those metrics.

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
| POST | `/api/takedown/contact-suggestions` | Search public pages on the result website for contact emails | Bearer token |
| POST | `/api/takedown/preview` | Prepare preview using an editable recipient without sending email | Bearer token |
| POST | `/api/legal-notice` | Alias for the no-send notice preview | Bearer token |
| POST | `/api/takedown/email` | Submit a reviewed preview in test mode or via Resend | Bearer token |

## Important configuration and scope

Backend environment settings are documented in backend/.env.example; frontend settings are documented in frontend/.env.example. Local operator accounts are stored in a SQLite file ignored by Git, and session token hashes—not raw tokens—are stored in the database.

Configure CORS_ORIGINS to exactly match the frontend origins you use. The current notice workflow no longer assumes that every result belongs to Meta, Google, X, or TikTok. It checks public pages on the matched result host for visible contact emails and shows source links; if none are found, the recipient field remains editable for a manually verified address. An address discovered on a public page is only a suggestion, not confirmation that it is the designated legal or copyright department.

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
