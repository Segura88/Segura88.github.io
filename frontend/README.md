Frontend (React + Vite + TypeScript + Tailwind)

Setup (once):

# from project root
cd frontend
npm install

# Run dev server
npm run dev

Notes:
- The frontend expects the backend available at the same origin during development. If the backend runs on a different origin, adjust proxy in `vite.config.ts` or set `VITE_API_BASE` env var in `.env`.
- The /write page expects a query param `token` with the token received in email. It will call `GET /token/{token}` to validate and then POST `/weekly-memory` with `Authorization: Bearer <token>`.

Run backend + frontend locally (quick guide):

1. Start backend (in project root, venv activated):

```powershell
& "venv/Scripts/Activate.ps1"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

2. In a new shell, start frontend:

```powershell
cd frontend
npm install
npm run dev
```

The frontend dev server proxies API calls to http://localhost:8000 as configured in `vite.config.ts`.
