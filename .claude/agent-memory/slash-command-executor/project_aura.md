---
name: AURA Platform Architecture
description: Full-stack beauty intelligence platform for Naturals salon chain (750+ locations). Hackathon project covering 60 problem statements across 6 tracks with 63 AI agents.
type: project
---

AURA is the hackathon entry for Naturals BeautyTech (StartupTN x Naturals 2026). It is a production-grade full-stack platform.

**Why:** Hackathon covering 60 real operational pain points across 6 challenge tracks. Built to demonstrate enterprise-level implementation depth.

**How to apply:** When suggesting new features or fixes, always map them to one of the 60 PS codes (PS-01.01 to PS-06.10). The platform is largely complete — focus on polish, integration gaps, and missing edge cases.

## Architecture at a Glance

- **Frontend:** `frontend/` — React 19 + TypeScript 5, Vite 8, Tailwind CSS, Zustand (auth), TanStack Query v5, Framer Motion, Three.js/R3F, Recharts, PWA-enabled
- **Backend:** `backend/app/` — FastAPI 0.115, SQLAlchemy 2 async, PostgreSQL (prod) / SQLite (dev), Alembic, Celery + Redis
- **AI:** OpenAI GPT-4o-mini or Google Gemini 2.0 Flash — switchable via `AI_PROVIDER` env var
- **Auth:** JWT HS256, 15-min access / 7-day refresh tokens, race-safe refresh in axios interceptor
- **Storage:** MinIO / Supabase Storage (configurable)
- **PWA:** NetworkFirst caching for `/api/v1/*`, InstallPrompt component

## Backend Structure

- `app/main.py` — FastAPI app, 33 routers registered, 63 agents auto-registered as endpoints
- `app/agents/` — 6 track files, each with 10-12 agents, all using real SQLAlchemy queries
- `app/routers/` — 33 dedicated CRUD routers for every domain
- `app/models/` — 32 ORM models (soft-deletes via `is_deleted`)
- `app/services/` — ai_service (GPT/Gemini), weather_service (Open-Meteo), email_service, analytics_service, sns_service (WhatsApp), skintone_service
- `app/database.py` — Cross-DB type helpers: FlexibleJSON, FlexibleARRAY, FlexibleEnum (SQLite ↔ PG)

## Frontend Structure

- `src/pages/` — 9 role-based sections: admin, customer, stylist, manager, franchise, regional, analytics, mirror, soulskin, shared, public, locations
- `src/stores/authStore.ts` — Zustand with localStorage persistence, role-based redirect helpers
- `src/config/api.ts` — Axios client with race-safe token refresh interceptor
- `src/types/index.ts` — Comprehensive TypeScript types for all domain entities
- `src/components/` — TiltCard, Icon3D, BeautyScoreRing, AuraPulse, ArchetypeBadge, ClimateAlertBanner, ErrorBoundary, Sidebar

## Key Domain Features

- **Beauty Passport** — 40+ customer diagnostic fields (hair, skin, scalp, allergies, goals)
- **SOULSKIN Engine** — Emotion-to-beauty archetype system (phoenix/river/moon/bloom/storm), AI soul readings
- **AR Mirror** — Three.js/R3F based virtual try-on
- **Digital Beauty Twin** — Health timeline, future skin projections
- **6 Roles** — super_admin, regional_manager, franchise_owner, salon_manager, stylist, customer
- **Loyalty Program** — AURA Points with tiers (bronze→silver→gold→platinum), referral codes, 100 welcome points on signup
- **Agent System** — 63 agents exposed as FastAPI endpoints under `/api/v1/agents/`, discoverable via `/api/v1/agents/registry`

## DB Notes

- Soft deletes: `is_deleted` flag + `deleted_at` timestamp on all major models
- UUID primary keys (string 36)
- Async sessions via `get_db` dependency (commit on success, rollback on exception)
- SQLite for dev (aura.db), Supabase PostgreSQL for prod
