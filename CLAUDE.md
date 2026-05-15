# AURA Project Brain

## What This Is
AURA — AI-Unified Reasoning Architecture. A full-stack beauty intelligence platform for Naturals salon chain (750+ locations). 63 AI agents across 6 business tracks.

## Stack
- **Frontend**: React 19 + TypeScript 5, Vite 8, Tailwind CSS, Zustand, TanStack Query v5, Zod 4, Framer Motion, Three.js/R3F
- **Backend**: FastAPI 0.115, SQLAlchemy 2 (async), PostgreSQL (Supabase prod) / SQLite (dev), Alembic, Celery + Redis
- **AI**: OpenAI GPT-4o / Google Gemini (switchable via `AI_PROVIDER` env)
- **Auth**: JWT (HS256, 15-min access / 7-day refresh)
- **Storage**: MinIO / Supabase Storage
- **Email**: SendGrid
- **PWA**: vite-plugin-pwa, NetworkFirst for `/api/v1/*`

## Project Layout
```
natural/
├── frontend/          React app (src/pages, src/components, src/hooks)
│   └── src/pages/    admin, customer, mirror, soulskin, stylist, manager, franchise, regional, analytics, shared, public
├── backend/
│   └── app/
│       ├── agents/   63 agents across track1–track6
│       ├── models/   32 SQLAlchemy ORM models
│       ├── routers/  20+ FastAPI routers under /api/v1
│       ├── services/ ai_service, weather_service, email_service, analytics
│       ├── schemas/  Pydantic request/response schemas
│       └── tasks/    Celery tasks
```

## Dev Commands
```bash
# Frontend
cd frontend && npm run dev        # Vite dev server (port 5173)
cd frontend && npm run build      # Production build
cd frontend && npm run lint       # ESLint

# Backend
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m pytest --tb=short -q
cd backend && alembic upgrade head

# Full stack
cd frontend && npm install
cd backend && pip install -r requirements.txt
```

## Conventions
- TypeScript strict mode, no `any` types
- React: functional components + hooks only, no class components
- Forms: React Hook Form + Zod on frontend; Pydantic schemas on backend
- State: Zustand for global state, TanStack Query for server state
- Styling: Tailwind CSS, dark-mode first, `cn()` for conditional classes
- DB: all operations async (AsyncSession), soft deletes via `is_deleted`
- API prefix: `/api/v1`, all routes tagged and documented
- AI agents: registered in track modules, printed on startup
- No `any`, functions under 50 lines, no prop drilling
- Images: use standard `<img>` (no Next.js here), lazy-load where appropriate

## Environment
- Backend `.env` at `backend/.env` (never commit)
- Frontend env via Vite `import.meta.env` (prefix `VITE_`)
- DB: `DATABASE_URL` in backend config (Supabase URL or `sqlite+aiosqlite:///./aura.db`)

## Git Commits
- Never add `Co-Authored-By: Claude` or any Claude/AI attribution lines to commit messages
- Commits should only show the human author (DHILIP S E)
