# AURA — Project Brain & Flow Guide

> AI-Unified Reasoning Architecture | Naturals Salon Chain (750+ locations)

---

## What Is This?

AURA is a full-stack beauty intelligence platform. It connects 6 roles (Customer → Stylist → Manager → Franchise → Regional → Admin) through a unified React frontend, FastAPI backend, and 64 AI agents across 6 business tracks.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript 5, Vite 8, Tailwind CSS |
| State | Zustand (auth/UI), TanStack Query v5 (server state) |
| Forms | React Hook Form + Zod 4 |
| Animation | Framer Motion, Three.js / R3F |
| Backend | FastAPI 0.115, SQLAlchemy 2 (async) |
| Database | PostgreSQL (Supabase prod) / SQLite (dev) |
| Migrations | Alembic |
| Queue | Celery + Redis |
| AI | OpenAI GPT-4o / Google Gemini (switch via `AI_PROVIDER`) |
| Auth | JWT — 15-min access token, 7-day refresh |
| Storage | MinIO / Supabase Storage |
| Email | SendGrid |
| PWA | vite-plugin-pwa, NetworkFirst for `/api/v1/*` |

---

## Project Layout

```
natural/
├── frontend/
│   └── src/
│       ├── pages/          70+ role-based pages
│       ├── components/     layout, UI, error boundary
│       ├── stores/         Zustand auth store
│       ├── hooks/          custom React hooks
│       ├── lib/            offline DB, utilities
│       └── config/         API base URL
│
├── backend/
│   └── app/
│       ├── agents/         64 AI agents (track1–track6)
│       ├── models/         31 SQLAlchemy ORM models
│       ├── routers/        36 FastAPI routers under /api/v1
│       ├── schemas/        Pydantic request/response
│       ├── services/       ai_service, weather, email, analytics
│       └── tasks/          12 Celery async task modules
```

---

## User Roles & Access Flow

```
Public (no auth)
  └── / Landing → /login → /register
      └── /salons  (map)
      └── /wait/:locationId
      └── /consult/:bookingId

Authenticated (JWT required)
  ├── customer      → /customer/*
  ├── stylist       → /stylist/*
  ├── salon_manager → /manager/*
  ├── franchise_owner → /franchise/*
  ├── regional_manager → /regional/*
  └── super_admin   → /admin/*
```

Access control is enforced by `<ProtectedRoute role="...">` in `App.tsx`. Wrong role → redirect.

---

## Frontend Pages by Role

### Customer (11 pages)
| Route | Page | Purpose |
|---|---|---|
| /customer | CustomerDashboard | Home hub, quick actions |
| /customer/passport | BeautyPassport | AI beauty profile history |
| /customer/twin | BeautyTwinTimeline | Digital twin evolution |
| /customer/mirror | ARMirrorPage | AR virtual try-on |
| /customer/bookings | CustomerBookings | View/manage bookings |
| /customer/book | BookNew | Book an appointment |
| /customer/skintone | SkinToneBot | AI skin analysis |
| /customer/journey | BeautyJourney | Personalized beauty roadmap |
| /customer/soulskin | SoulskinFlow | Holistic skin wellness |
| /customer/homecare | HomecarePage | At-home routine builder |
| /customer/loyalty | LoyaltyDashboard | AURA Points & rewards |
| /customer/profile | CustomerProfilePage | Profile settings |

### Stylist (8 pages)
| Route | Page | Purpose |
|---|---|---|
| /stylist | StylistDashboard | Daily schedule, queue |
| /stylist/customers | StylistCustomers | Client list |
| /stylist/session/:id | LiveSession | Active session with AI assist |
| /stylist/performance | StylistPerformance | KPIs, ratings |
| /stylist/training | StylistTraining | AI-guided upskilling |
| /stylist/voice | VoiceAssistant | Hands-free AI commands |
| /stylist/aurascore | AuraScoreDashboard | AURA quality score |

### Salon Manager (15 pages)
| Route | Page | Purpose |
|---|---|---|
| /manager | ManagerDashboard | Location overview |
| /manager/team | TeamManagement | Staff scheduling |
| /manager/bookings | Bookings | Appointment management |
| /manager/queue | QueueManagement | Real-time queue |
| /manager/quality | QualityDashboard | Service quality scores |
| /manager/soulskin | SoulskinAnalytics | Skin analytics for location |
| /manager/sops | SOPManagement | Standard procedures |
| /manager/trends | TrendIntelligence | Local beauty trends |
| /manager/inventory | InventoryForecast | AI inventory prediction |
| /manager/eco | EcoTracker | Sustainability tracking |
| /manager/feedback | FeedbackPage | Customer feedback |
| /manager/alerts | AlertsHubPage | Smart alerts |
| /manager/settings | LocationSettingsPage | Location config |

### Franchise Owner (8 pages)
| Route | Page | Purpose |
|---|---|---|
| /franchise | FranchiseDashboard | Multi-location overview |
| /franchise/performance | FranchisePerformanceDashboard | Revenue & growth |
| /franchise/locations | LocationsPage | All owned locations |
| /franchise/compare | CompareLocationsPage | Side-by-side comparison |

### Regional Manager (9 pages)
Regional-level KPIs, trends, staff, and location performance across a zone.

### Super Admin (18 pages)
Full system control: Users, RBAC, AI Engine, System Config, BI Dashboard, all analytics.

---

## Backend API Routers

All routes prefixed with `/api/v1`.

### Auth & Users
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/customers
GET  /api/v1/staff
GET  /api/v1/roles
```

### Core Salon Operations
```
/bookings       — create, list, cancel, reschedule
/sessions       — live session lifecycle
/queue          — real-time queue management
/services       — service catalog
/locations      — salon locations + settings
/sops           — standard operating procedures
/consultation   — pre-service AI consultation
/waittime       — wait time estimation
```

### Customer Experience
```
/journey        — personalized beauty journey
/homecare       — homecare routine recommendations
/loyalty        — AURA points + rewards
/soulskin       — holistic skin wellness data
/notifications  — push/email/WhatsApp alerts
/chatbot        — AI chat widget
/feedback       — NPS + satisfaction surveys
```

### AI & Beauty Science
```
/mirror         — AR Smart Mirror sessions
/twin           — Beauty Digital Twin
/twin-timeline  — Twin evolution history
/mood           — Mood-based service matching
/skintone       — AI skin tone analysis
/aurascore      — AURA quality score
/upsell         — AI upsell suggestions
/allergy        — Chemical allergy safety gate
```

### Business Intelligence
```
/analytics      — Revenue, foot traffic, trends
/trends         — Local + global trend intelligence
/quality        — Quality scoring + complaints
/training       — Staff training modules
/climate        — Weather-adjusted service recommendations
/eco            — Sustainability metrics
/voice          — Voice assistant sessions
/franchise-dashboard — Multi-location franchise BI
```

### AI Agent Discovery
```
GET /api/v1/agents/registry           — All 64 agents
GET /api/v1/agents/registry/{track}   — Agents by track (1–6)
GET /api/v1/agents/ps/{ps_code}       — Find agent by problem statement code
```

---

## 64 AI Agents — 6 Business Tracks

### Track 1 — Standardizing Salon Experience (12 agents)
```
pre_service_consultation    → AI brief before stylist arrives
complete_consultation       → Post-service summary
sop_live_guide              → Real-time SOP guidance during service
sop_step_complete           → Validates each SOP step
quality_score_compute       → Automated quality scoring
complaint_root_cause        → Root cause analysis for complaints
branch_live_status          → Live location health check
service_readiness_check     → Pre-open readiness gate
customer_handover_brief     → Stylist handover card
chemical_safety_gate        → Allergy + chemical risk check
knowledge_capture           → Captures stylist learnings
knowledge_search            → Retrieves SOPs and guides
```

### Track 2 — Reducing Staff Dependency (11 agents)
```
staff_roaming_assistant     → Assigns tasks to available staff
task_assignment_optimize    → Optimal task distribution
schedule_shift_plan         → AI shift scheduling
attendance_anomaly_detect   → Detects unusual patterns
performance_coaching_prompt → Coaching nudges for staff
attrition_risk_scan         → Predicts staff churn risk
payroll_compliance_check    → Flags payroll issues
staff_recruitment_funnel    → AI-screened hiring pipeline
staff_onboarding_flow       → Automated onboarding
staff_engagement_survey     → Micro-pulse surveys
roster_absence_cover        → Auto-fills absent slot
```

### Track 3 — Hyper-Personalized Beauty (10 agents)
```
ai_hair_skin_diagnosis      → Diagnoses hair + skin from photo
archetype_classifier        → Beauty personality archetype
mood_color_match            → Mood → color recommendation
journey_plan_generate       → 12-week beauty journey
ai_consultation_coach       → Live consultation AI co-pilot
beauty_passport_full        → Full beauty history profile
soulskin_engine_upgrade     → Skin wellness deep analysis
client_transition_plan      → Service transition roadmap
ai_upsell_suggestions       → Context-aware upsell
preference_learning_loop    → Continuous preference refinement
```

### Track 4 — AI-Based Trend Prediction (10 agents)
```
celebrity_trend_alert       → Detects celebrity-driven trends
social_trend_radar          → Social media trend scanner
seasonal_trend_forecast     → Season-ahead predictions
niche_trend_identify        → Emerging niche trends
competitor_intelligence     → Competitor service monitoring
competitive_listing         → Comparative service analysis
cross_branch_benchmark      → Inter-branch performance
campaign_recommender        → AI campaign suggestions
micro_trend_accelerate      → Fast-track micro trends
regional_macro_forecast     → Zone-level macro trends
```

### Track 5 — AI Customer Experience (10 agents)
```
ambient_intelligence        → Environment-aware service adjust
wait_psychology_optimize    → Reduces perceived wait time
queue_flow_predict          → Predicts queue peaks
experience_moment_capture   → Captures memorable moments
nps_pulse_survey            → Automated NPS collection
sentiment_analysis_feedback → Analyzes review sentiment
ai_complaint_resolution     → Auto-resolves minor complaints
checkout_cross_sell         → Checkout product suggestions
loyalty_engagement_engine   → Loyalty nudges + campaigns
notification_channel_optimize → Best channel per customer
```

### Track 6 — Salon Business Intelligence (10 agents)
```
branch_health_predictor     → Predicts branch performance dip
customer_ltv_model          → Customer lifetime value
staff_productivity_dashboard → Real-time staff efficiency
revenue_forecast_dashboard  → Rolling revenue forecast
inventory_demand_forecast   → AI inventory planning
allergy_safety_check        → Allergy cross-reference
capacity_rebalance          → Load balancing across branches
climate_adjust_service      → Weather-driven service push
franchise_bi_dashboard      → Franchise rollup analytics
franchise_live_compare      → Real-time location comparison
language_service_brief      → Multi-language service brief
```

---

## Data Models (31 entities)

```
Identity         User (6 roles), CustomerProfile, StaffProfile
Booking          Booking, Session, Queue, Scheduling
Services         Service, Location, SOP, Consultation
Beauty Science   Soulskin, SkinTone, ARMirror, DigitalTwin, Mood
                 Recommendation, Handover
Intelligence     Analytics, Trend, Quality, Feedback, Training
Growth           Loyalty, Homecare, Knowledge, Campaign, Notification
Operations       Inventory, Climate, WaitingExperience, Followup
```

All models use:
- UUID primary keys
- `TimestampMixin` (created_at, updated_at)
- `SoftDeleteMixin` (is_deleted flag — no hard deletes)
- Enum-based role and status fields

---

## Request → Response Flow

```
Browser (React)
    │
    ├── TanStack Query / Zustand
    │       └── fetch /api/v1/...
    │
    ▼
FastAPI (port 8000)
    │
    ├── JWT Middleware → verify token → extract role
    ├── CORS Middleware
    ├── Router → validates Pydantic schema
    │       └── calls service/agent
    │
    ├── Agent Route (/api/v1/agents/*)
    │       └── AI agent → calls OpenAI / Gemini
    │               └── returns structured JSON
    │
    ├── CRUD Route
    │       └── AsyncSession → SQLAlchemy query → PostgreSQL
    │
    └── Response → Pydantic schema → JSON → browser
```

---

## Auth Flow

```
1. POST /api/v1/auth/login  {email, password}
2. Server returns {access_token, refresh_token, role}
3. Frontend stores tokens in Zustand (useAuthStore)
4. Every API request: Authorization: Bearer <access_token>
5. On 401 → POST /api/v1/auth/refresh → new access token
6. Logout → clear Zustand state
```

---

## Booking Flow (Customer)

```
/customer/book → BookNew.tsx
    │
    ├── Select location → GET /api/v1/locations
    ├── Select service  → GET /api/v1/services
    ├── Select slot     → GET /api/v1/bookings/slots
    │
    ▼
POST /api/v1/bookings  → creates Booking record
    │
    ├── Notification sent (email/WhatsApp)
    ├── Queue entry created
    └── AI consultation triggered (Track 1 agent)
```

---

## Live Session Flow (Stylist)

```
/stylist/session/:id → LiveSession.tsx
    │
    ├── GET /api/v1/sessions/:id  → load session + customer brief
    ├── AI SOP guide active       → sop_live_guide agent
    ├── Voice assistant available → /api/v1/voice
    │
    ├── During service:
    │   ├── sop_step_complete validates each step
    │   ├── quality_score_compute updates score live
    │   └── ai_upsell_suggestions recommends products
    │
    └── On complete:
        ├── complete_consultation agent → summary
        ├── Booking status → completed
        ├── NPS survey triggered
        └── Loyalty points awarded
```

---

## Dev Commands

```bash
# Frontend
cd frontend && npm install
cd frontend && npm run dev        # http://localhost:5173
cd frontend && npm run build
cd frontend && npm run lint

# Backend
cd backend && pip install -r requirements.txt
cd backend && alembic upgrade head
cd backend && uvicorn app.main:app --reload --port 8000

# Tests
cd backend && python -m pytest --tb=short -q
```

---

## Environment Variables

```bash
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./aura.db   # or Supabase URL
SECRET_KEY=your-jwt-secret
AI_PROVIDER=openai                            # or gemini
OPENAI_API_KEY=...
SENDGRID_API_KEY=...
REDIS_URL=redis://localhost:6379

# frontend/.env (prefix VITE_)
VITE_API_URL=http://localhost:8000
```

---

## Stats

| Item | Count |
|---|---|
| Frontend Pages | 70+ |
| Backend Routers | 36 |
| AI Agents | 64 |
| ORM Models | 31 |
| User Roles | 6 |
| Business Tracks | 6 |
| API Endpoints | 100+ |
