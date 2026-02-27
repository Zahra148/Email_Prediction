# UMA Health Demo App

Demo-ready scaffold with:
- **Frontend:** Next.js (App Router + TypeScript)
- **Backend:** FastAPI (Python 3.10+)

## Routes

### Frontend
- `/` landing page
- `/upload` image + location + goal form
- `/results` renders returned plan

### Backend
- `POST /v1/plan`
- `POST /v1/render`

## Quick start

### 1) Install dependencies

```bash
npm install
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run both services (demo mode)

```bash
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Environment

Set backend URL for the frontend if needed:

```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Stub plan response

`POST /v1/plan` returns:
- `layout` array
- `nutrient_diversity_score`
- `savings_monthly_usd`
- `explanation`

This keeps the implementation minimal and optimized for Demo Day speed.
