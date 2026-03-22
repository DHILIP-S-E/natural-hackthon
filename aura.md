# AURA — UNIFIED SALON INTELLIGENCE PLATFORM
## MASTER SYSTEM DESIGN DOCUMENT — VERSION 2.0
### Naturals BeautyTech Hackathon 2026 | Challenge 5: Open Innovation
### Stack: FastAPI + React + SQLAlchemy + PostgreSQL | Full PWA

---

> **HOW TO USE THIS DOCUMENT**
> This is a design-only document. No code is written here. Every section describes
> what to build, how it behaves, what data it holds, and what rules govern it.
> Feed this to an AI coding tool and it will produce production-ready output.
> Version 2.0 adds: AI BeautyVerse modules, MirrorMind AI, SOULSKIN Emotion Engine,
> Digital Beauty Twin, AI Smart Mirror, Mood Detection, and full PWA specification.

---

## CHANGE LOG: V1 → V2

| What's New | Where |
|---|---|
| SOULSKIN Emotion Engine (soul reading, archetypes, experience design) | Part 1, Part 3, Part 5 |
| AI Smart Mirror (AR try-on, virtual color, hairstyle preview) | Part 1, Part 3, Part 5 |
| MirrorMind AI (emotion detection, lifestyle intelligence, future simulation) | Part 1, Part 3, Part 5 |
| Digital Beauty Twin (3D face model, long-term simulation) | Part 3, Part 5 |
| AI Mood Detection (computer vision mood → service recommendation) | Part 3, Part 5 |
| Smart Queue & Experience Optimizer | Part 3, Part 5 |
| AI Beauty Journey Planner (3-month/6-month roadmap) | Part 3, Part 5 |
| Climate-Aware Recommendations (real-time weather + AQI integration) | Part 3, Part 5 |
| SOULSKIN Soul Journal (per-customer emotional beauty diary) | Part 3, Part 5 |
| Full PWA Specification (offline, install prompts, service worker details) | Part 1, Part 9 |
| New API endpoints for all new modules | Part 4 |
| New database tables for all new modules | Part 3 |
| New pages for all new modules | Part 5 |

---

## PART 1: SYSTEM OVERVIEW

### 1.1 What is AURA?

AURA is a unified, AI-powered salon intelligence platform that solves all 6 Naturals BeautyTech Hackathon challenge tracks inside one system. It is not a prototype. It is a production-ready system designed to run at scale across 750+ salon locations.

AURA is built on three intelligence layers:

**Layer 1 — PHYSICAL INTELLIGENCE**
Computer vision, AI diagnostics, skin/hair analysis. Reads what the body shows.

**Layer 2 — EMOTIONAL INTELLIGENCE (SOULSKIN)**
Emotion detection, mood analysis, soul reading, archetype assignment. Reads what the soul carries. This is the world's first Emotion-to-Beauty Intelligence System.

**Layer 3 — PREDICTIVE INTELLIGENCE**
Trend forecasting, attrition prediction, revenue forecasting, demand planning. Reads what tomorrow will need.

All three layers share one data backbone. Every insight from one layer enriches the others.

### 1.2 The Complete User Journey (All Layers)

```
STEP 1  → Customer walks in or books via WhatsApp / App / PWA
STEP 2  → Smart Queue system estimates wait time → WhatsApp notification sent
STEP 3  → AI scans face + hair (Beauty Passport updated)
           → Skin type, hair condition, damage level, scalp health
           → Emotion detection from facial expression (mood reading)
           → Digital Beauty Twin updated (3D face model)
STEP 4  → SOULSKIN Soul Reading activated
           → 3 questions asked (song / colour / feeling word)
           → Archetype assigned (Phoenix / River / Moon / Bloom / Storm)
           → Complete sensory experience designed for this customer today
STEP 5  → AI Smart Mirror experience
           → Customer virtually tries hairstyles, colors, makeup on own face
           → Climate-aware recommendations shown (weather + AQI)
           → Before simulation saved to Beauty Passport
STEP 6  → Stylist receives AI Stylist Assistant on tablet
           → Real-time SOP guidance + SOULSKIN stylist script
           → Customer-specific coaching (hair porosity, skin sensitivity, mood state)
           → Chemical ratios auto-calculated for this customer's hair
STEP 7  → Service executed → Steps tracked → Timer running
           → Quality score auto-calculated on completion
           → Before/after photos captured → added to Digital Beauty Twin
STEP 8  → AI Beauty Journey Planner generates 3-month roadmap
           → Personalized home care plan sent via WhatsApp
           → Soul Journal entry saved with archetype + transformation note
STEP 9  → All data flows to Franchise BI Dashboard
           → Manager sees: quality scores, sentiment, attrition risk, trends
STEP 10 → Trend Engine learns from booking surge data
           → New trend detected → inventory + training alert generated
STEP 11 → Staff skill tracked → training ROI measured → attrition predicted
           → Weekly attrition risk update for all staff
```

### 1.3 The 8 Intelligence Modules

```
MODULE 1: BEAUTY PASSPORT       → Digital beauty identity. AI diagnostics. Lifelong profile.
MODULE 2: SOULSKIN ENGINE       → Emotion-to-beauty. Soul reading. Archetype. Sensory design.
MODULE 3: AI SMART MIRROR       → AR try-on. Virtual hairstyles. Makeup simulation.
MODULE 4: DIGITAL BEAUTY TWIN   → 3D face model. Future skin simulation. Long-term tracking.
MODULE 5: AI STYLIST ASSISTANT  → Real-time SOP guidance. AI co-pilot for stylists.
MODULE 6: TREND INTELLIGENCE    → Social listening. Demand forecasting. Proactive alerts.
MODULE 7: STAFF INTELLIGENCE    → Skill mapping. Training ROI. Attrition prediction.
MODULE 8: SALON BI DASHBOARD    → Revenue. Quality. Retention. Franchise benchmarking.
```

### 1.4 Tech Stack — Full Production

```
BACKEND:
  Runtime:         Python 3.11+
  Framework:       FastAPI (async) — all endpoints async
  ORM:             SQLAlchemy 2.0 (async sessions, connection pooling)
  Database:        PostgreSQL 16 (primary, ACID compliant)
  Vector DB:       pgvector extension on PostgreSQL (beauty profile embeddings)
  Cache:           Redis 7 (sessions, queues, rate limits, real-time state)
  Auth:            JWT RS256 (access token 15min) + Refresh (7 days, httpOnly cookie)
  File Storage:    AWS S3 / Cloudflare R2 (images, videos, 3D models)
  Background:      Celery + Redis (AI analysis, notifications, reports, trend detection)
  Email:           SendGrid
  SMS/WhatsApp:    Twilio + Meta WhatsApp Business API
  AI/LLM:          OpenAI GPT-4o (SOULSKIN soul reading, SOP guidance, home care plans)
  Vision AI:       MediaPipe (in-browser face/hair detection) + custom PyTorch models
  Emotion AI:      FER (Facial Expression Recognition) model + custom fine-tuned model
  AR/3D:           Three.js backend model generation for Digital Beauty Twin
  Weather API:     OpenWeatherMap API (real-time climate data per location city)
  Migrations:      Alembic
  Testing:         pytest + httpx

FRONTEND:
  Framework:       React 18 + TypeScript
  Routing:         React Router v6 (nested, protected routes)
  State:           Zustand (global) + TanStack Query (server state)
  UI Base:         shadcn/ui + Radix UI
  Styling:         Tailwind CSS + CSS custom properties (design tokens)
  Charts:          Recharts + D3.js
  3D/Animation:    Three.js (landing + Digital Beauty Twin) + Framer Motion
  AR Mirror:       MediaPipe Face Mesh + custom canvas rendering (WebGL)
  Forms:           React Hook Form + Zod
  Tables:          TanStack Table v8
  Camera:          MediaPipe (face mesh, hair segmentation, expression detection)
  PWA:             Workbox 7 (full service worker, offline cache, background sync)
  PWA Features:    Install prompt, push notifications, offline-first stylist session
  Build:           Vite + vite-plugin-pwa

PWA SPECIFICATION (Full Detail — see Part 9):
  - App installable on Android, iOS (Add to Home Screen), Desktop (Chrome)
  - Offline-capable pages: Stylist session, Today's schedule, Customer passport view
  - Push notifications: booking reminders, trend alerts, quality flags
  - Background sync: session steps sync when internet restored
  - App manifest: AURA brand colors, splash screen, icon set
  - Service worker strategy: Cache-first for static, Network-first for API
  - Works on: Android (Chrome), iOS (Safari 16.4+), Desktop Chrome/Edge

INFRASTRUCTURE:
  Cloud:           AWS Mumbai (ap-south-1) — lowest latency for India
  Compute:         ECS Fargate (auto-scaling containers)
  Frontend:        S3 + CloudFront CDN (global edge for PWA assets)
  Database:        RDS PostgreSQL Multi-AZ (automatic failover)
  Cache:           ElastiCache Redis (cluster mode)
  ML Models:       S3 storage + SageMaker inference endpoints (custom models)
  CDN:             CloudFront (static assets, images, PWA cache)
  Monitoring:      Sentry (frontend + backend errors) + CloudWatch + Grafana
  Security:        AWS WAF + VPC + KMS (encryption at rest) + Secrets Manager
  CI/CD:           GitHub Actions (test → build → deploy on merge to main)
```

### 1.5 ACID Compliance

Every financial transaction, booking, and critical data write uses full ACID:
- **Atomicity**: SQLAlchemy session wraps all related writes. Any failure = full rollback.
- **Consistency**: PostgreSQL constraints + foreign keys + SQLAlchemy validators.
- **Isolation**: READ COMMITTED for reads. SERIALIZABLE for payments and bookings.
- **Durability**: PostgreSQL WAL. RDS multi-AZ. Point-in-time recovery.

---

## PART 2: USER ROLES & RBAC

### 2.1 The Six Roles

```
ROLE 1: SUPER_ADMIN
  Who:    Naturals corporate team.
  Sees:   Everything. All locations, all data.
  Can do: Create/edit/delete anything. Full system config. All reports.

ROLE 2: REGIONAL_MANAGER
  Who:    Manages a geographic region (e.g., South Tamil Nadu).
  Sees:   All locations in their region only.
  Can do: View/edit location data, staff, quality scores in their region.

ROLE 3: FRANCHISE_OWNER
  Who:    Owns one or more franchise locations.
  Sees:   Their owned location(s) only.
  Can do: View full data for their location. Manage staff. View financials.

ROLE 4: SALON_MANAGER
  Who:    Day-to-day manager of one specific location.
  Sees:   Their location only.
  Can do: Manage bookings, staff, quality scores, SOPs, reports.

ROLE 5: STYLIST
  Who:    Salon service staff.
  Sees:   Their own schedule, assigned customers, their performance.
  Can do: Follow SOP guidance, run SOULSKIN session, view their quality scores.

ROLE 6: CUSTOMER
  Who:    End client.
  Sees:   Their own Beauty Passport, bookings, SOULSKIN journal, Journey Plan.
  Can do: Book, scan, try AR mirror, view passport, read soul journal.
```

### 2.2 Full Permission Matrix

| Feature                        | SUPER | REGIONAL | FRANCHISE | MANAGER | STYLIST | CUSTOMER |
|-------------------------------|-------|----------|-----------|---------|---------|----------|
| View all locations             | ✅    | Region   | Own       | Own     | ❌      | ❌       |
| Create/delete locations        | ✅    | ❌       | ❌        | ❌      | ❌      | ❌       |
| Create staff                   | ✅    | ✅       | ✅        | ❌      | ❌      | ❌       |
| View/edit staff                | ✅    | Region   | Own       | Own     | Self    | ❌       |
| Delete staff                   | ✅    | ❌       | ❌        | ❌      | ❌      | ❌       |
| View customers                 | ✅    | Region   | Own       | Own     | Assigned| Self     |
| View Beauty Passport           | ✅    | ✅       | ✅        | ✅      | ✅      | Self     |
| View Soul Journal              | ✅    | ✅       | ✅        | ✅      | ✅      | Self     |
| Run SOULSKIN session           | ✅    | ✅       | ✅        | ✅      | ✅      | ❌       |
| View Digital Beauty Twin       | ✅    | ✅       | ✅        | ✅      | ✅      | Self     |
| Use AR Smart Mirror            | ✅    | ✅       | ✅        | ✅      | ✅      | ✅       |
| View financials                | ✅    | Region   | Own       | Own     | ❌      | ❌       |
| Manage SOPs                    | ✅    | ❌       | ❌        | ✅      | ❌      | ❌       |
| View trend intelligence        | ✅    | ✅       | ✅        | ✅      | ❌      | ❌       |
| Use AI Stylist Assistant       | ✅    | ✅       | ✅        | ✅      | ✅      | ❌       |
| View quality scores            | ✅    | Region   | Own       | Own     | Self    | ❌       |
| Export reports                 | ✅    | Region   | Own       | Own     | ❌      | ❌       |
| System config                  | ✅    | ❌       | ❌        | ❌      | ❌      | ❌       |
| Book appointment               | ✅    | ✅       | ✅        | ✅      | ✅      | ✅       |
| View mood detection data       | ✅    | Region   | Own       | Own     | Own     | Self     |
| View attrition predictions     | ✅    | Region   | Own       | Own     | ❌      | ❌       |
| View training management       | ✅    | ✅       | ✅        | ✅      | View    | ❌       |
| View Beauty Journey Plan       | ✅    | ✅       | ✅        | ✅      | ✅      | Self     |

### 2.3 RBAC Rules

- Every FastAPI route: `Depends(require_permission("permission_key"))`
- Every React route: `<ProtectedRoute allowedRoles={[...]} />`
- Every sidebar item: conditionally rendered by role
- PostgreSQL Row Level Security (RLS) as backend-level defense
- All permission checks on backend. Frontend gating is UX only.

---

## PART 3: DATABASE SCHEMA — ALL TABLES

### Design Principles
- All PKs: UUID (prevents enumeration attacks)
- All tables: created_at, updated_at (auto-managed)
- Soft deletes everywhere: is_deleted + deleted_at
- Money fields: DECIMAL(12,2) — never FLOAT
- All enums: native PostgreSQL ENUM types
- All timestamps: UTC stored, timezone-converted on display
- JSONB for structured flexible data
- pgvector for AI embeddings (similarity search)

---

#### TABLE: users
Core identity for every person in the system.

```
id                    UUID, PK, gen_random_uuid()
email                 VARCHAR(255), UNIQUE, NOT NULL, indexed
phone                 VARCHAR(20), UNIQUE, indexed
password_hash         VARCHAR(255), NOT NULL
role                  ENUM: super_admin | regional_manager | franchise_owner |
                             salon_manager | stylist | customer
first_name            VARCHAR(100), NOT NULL
last_name             VARCHAR(100), NOT NULL
avatar_url            TEXT
is_active             BOOLEAN, default TRUE
is_verified           BOOLEAN, default FALSE
preferred_language    VARCHAR(5), default 'en'  (en | ta | hi | te | kn | ml)
push_token            TEXT  (PWA push notification token)
last_login_at         TIMESTAMP
is_deleted            BOOLEAN, default FALSE
deleted_at            TIMESTAMP
created_at, updated_at TIMESTAMP
```

---

#### TABLE: locations
Each Naturals salon outlet.

```
id                    UUID, PK
name                  VARCHAR(255), NOT NULL
code                  VARCHAR(20), UNIQUE  (NAT-TN-001)
address               TEXT, NOT NULL
city                  VARCHAR(100), NOT NULL
state                 VARCHAR(100), NOT NULL
pincode               VARCHAR(10)
region                VARCHAR(100)
latitude              DECIMAL(10,8)
longitude             DECIMAL(11,8)
phone                 VARCHAR(20)
email                 VARCHAR(255)
franchise_owner_id    UUID, FK → users.id
manager_id            UUID, FK → users.id
is_active             BOOLEAN, default TRUE
opening_date          DATE
monthly_revenue_target DECIMAL(12,2)
seating_capacity      INTEGER
operating_hours       JSONB  {"mon": {"open":"09:00","close":"20:00"}, ...}
smart_mirror_enabled  BOOLEAN, default FALSE
soulskin_enabled      BOOLEAN, default TRUE
climate_zone          VARCHAR(50)  (auto-set from lat/lng: tropical|arid|temperate|...)
is_deleted            BOOLEAN, default FALSE
created_at, updated_at TIMESTAMP
```

---

#### TABLE: staff_profiles
Extended profile for stylist, manager, franchise_owner users.

```
id                    UUID, PK
user_id               UUID, UNIQUE, FK → users.id, CASCADE DELETE
location_id           UUID, FK → locations.id
employee_id           VARCHAR(50), UNIQUE
designation           VARCHAR(100)
specializations       TEXT[]  ['hair_color','bridal','skin','nail','keratin']
skill_level           ENUM: L1 | L2 | L3
years_experience      DECIMAL(4,1)
joining_date          DATE
bio                   TEXT
is_available          BOOLEAN, default TRUE
weekly_off_day        VARCHAR(10)
attrition_risk_score  DECIMAL(3,2)  (0.00 to 1.00, ML-predicted weekly)
attrition_risk_label  ENUM: low | medium | high
current_rating        DECIMAL(3,2)  (rolling average)
total_services_done   INTEGER, default 0
total_revenue_generated DECIMAL(12,2), default 0
soulskin_certified    BOOLEAN, default FALSE  (completed SOULSKIN training)
languages_spoken      TEXT[]
portfolio_image_urls  TEXT[]
instagram_handle      VARCHAR(100)
created_at, updated_at TIMESTAMP
```

---

#### TABLE: customer_profiles  [THE BEAUTY PASSPORT]
The complete digital beauty identity for every customer.

```
id                    UUID, PK
user_id               UUID, UNIQUE, FK → users.id, CASCADE DELETE
preferred_location_id UUID, FK → locations.id
preferred_stylist_id  UUID, FK → staff_profiles.id

══ HAIR DIAGNOSTICS (AI-populated) ══
hair_type             VARCHAR(50)  straight | wavy | curly | coily
hair_texture          VARCHAR(50)  fine | medium | coarse
hair_porosity         VARCHAR(50)  low | normal | high
hair_density          VARCHAR(50)  thin | medium | thick
scalp_condition       VARCHAR(50)  normal | dry | oily | sensitive | dandruff
hair_damage_level     INTEGER      1 (healthy) to 5 (severely damaged)
natural_hair_color    VARCHAR(50)
current_hair_color    VARCHAR(50)
last_color_date       DATE
chemical_history      JSONB        [{treatment, date, products_used}]

══ SKIN DIAGNOSTICS (AI-populated) ══
skin_type             VARCHAR(50)  dry | oily | combination | normal | sensitive
skin_tone             VARCHAR(50)  fair | medium | dusky | dark
undertone             VARCHAR(50)  warm | cool | neutral
primary_skin_concerns TEXT[]       ['acne','pigmentation','wrinkles','dullness','dark_circles']
skin_sensitivity      VARCHAR(50)  low | medium | high
spf_usage             VARCHAR(50)  never | sometimes | daily
acne_severity         INTEGER      0 (none) to 5 (severe), AI-detected
pigmentation_level    INTEGER      0 to 5, AI-detected
wrinkle_score         INTEGER      0 to 5, AI-detected
hydration_estimate    VARCHAR(50)  dehydrated | normal | well-hydrated

══ LIFESTYLE (User-input + auto-fetched) ══
city                  VARCHAR(100)
local_uv_index        DECIMAL(4,2)  (auto-fetched, updated daily)
local_humidity        DECIMAL(4,2)  (auto-fetched, updated daily)
local_aqi             DECIMAL(6,2)  (auto-fetched, updated daily)
local_temp_celsius    DECIMAL(4,1)  (auto-fetched, updated daily)
climate_type          VARCHAR(50)   tropical | arid | temperate | cold
sun_exposure          VARCHAR(50)   low | medium | high
occupation_type       VARCHAR(100)  indoor_desk | outdoor_field | mixed
water_quality         VARCHAR(50)   soft | hard | very_hard
sleep_quality         VARCHAR(50)   poor | fair | good  (user-input, optional)
hydration_habit       VARCHAR(50)   low | medium | high  (user-input)
stress_level          VARCHAR(50)   low | medium | high  (user-input)
diet_type             VARCHAR(50)   vegetarian | vegan | non_vegetarian | mixed
upcoming_events       TEXT[]        ['wedding','engagement','party','photoshoot']

══ ALLERGIES & SAFETY ══
known_allergies       TEXT[]        ['PPD','ammonia','latex','fragrance','nickel']
product_sensitivities TEXT[]
patch_tested_on       DATE
patch_test_result     VARCHAR(50)   clear | reaction_noted

══ BEAUTY GOALS ══
primary_goal          VARCHAR(100)  'reduce_hair_fall'|'skin_brightening'|'hair_growth'
goal_timeline_weeks   INTEGER
goal_notes            TEXT
goal_progress_pct     INTEGER       0-100, AI-calculated based on visit history

══ EMOTIONAL PROFILE (SOULSKIN — aggregated over time) ══
dominant_archetype    VARCHAR(20)   phoenix | river | moon | bloom | storm | null
archetype_history     JSONB         [{archetype, date, session_id}]
emotional_sensitivity VARCHAR(50)   low | medium | high
preferred_touch_pressure VARCHAR(50) light | medium | deep
most_booked_mood_state TEXT[]       (top moods from soul journal entries)

══ DIGITAL TWIN METADATA ══
twin_model_url        TEXT          S3 URL of 3D face model
twin_last_updated     TIMESTAMP
twin_skin_timeline    JSONB         [{date, skin_score, image_url}]
simulation_enabled    BOOLEAN, default FALSE

══ METADATA ══
last_scan_at          TIMESTAMP
scan_image_url        TEXT
beauty_score          INTEGER       composite 0-100
passport_completeness INTEGER       % complete
total_visits          INTEGER, default 0
lifetime_value        DECIMAL(12,2)
first_visit_date      DATE
last_visit_date       DATE
profile_embedding     VECTOR(1536)  (pgvector — similarity matching)
created_at, updated_at TIMESTAMP
```

---

#### TABLE: soulskin_sessions
Each SOULSKIN emotional intelligence reading. One per customer visit (optional but encouraged).

```
id                    UUID, PK
booking_id            UUID, FK → bookings.id
customer_id           UUID, FK → customer_profiles.id
stylist_id            UUID, FK → staff_profiles.id
location_id           UUID, FK → locations.id

══ THE 3 QUESTIONS ══
question_1_song       TEXT          "Song that describes your life right now"
question_2_colour     VARCHAR(100)  "Colour that matches your mood today"
question_3_word       VARCHAR(100)  "One word you want to FEEL when you leave"

══ AI-GENERATED SOUL READING ══
soul_reading          TEXT          3-line poetic reading (LLM-generated)
archetype             VARCHAR(20)   phoenix | river | moon | bloom | storm
archetype_reason      TEXT          Why this archetype fits today

══ COMPLETE EXPERIENCE DESIGN (LLM-generated) ══
service_protocol      JSONB
  {
    "primary_treatment": "Balayage with toning gloss",
    "why_this_treatment": "Phoenix archetype needs bold colour transformation...",
    "modified_technique": "Apply from roots for maximum impact...",
    "duration_change": "+15 minutes — this soul needs space to breathe"
  }

colour_direction      JSONB
  {
    "colour_story": "Warm copper tones with honey highlights",
    "symbolism": "Represents the fire of reinvention starting from within",
    "finish": "Glossy, high-shine — confidence made visible"
  }

sensory_environment   JSONB
  {
    "aromatherapy": [{"scent":"bergamot","reason":"uplifts and energizes"},{"scent":"cedarwood","reason":"grounds and stabilizes"}],
    "lighting_start": "warm amber 2700K",
    "lighting_end": "bright natural 4000K — emerging into clarity",
    "music_arc": {"start_mood":"contemplative","end_mood":"empowered","songs":["Song1","Song2","Song3"]},
    "temperature": "slightly warm — this archetype needs comfort, not stimulation"
  }

touch_protocol        JSONB
  {
    "massage_pressure": "medium-to-deep",
    "emotional_reason": "Storm archetype carries tension in shoulders and scalp",
    "pressure_points": ["GV20 (crown)","GB21 (shoulder)","LI4 (hand)"],
    "scalp_ritual": "Begin with slow circular strokes at temples, work inward..."
  }

custom_formula        JSONB
  {
    "ingredients": [
      {"name":"Rosehip Oil","percentage":30,"reason":"Skin repair + emotional healing symbol"},
      {"name":"Argan Oil","percentage":25,"reason":"Moisture + strength for damaged hair"},
      {"name":"Lavender Essential Oil","percentage":5,"reason":"Calms storm archetype nervous system"},
      {"name":"Keratin Protein","percentage":35,"reason":"Rebuilds structural bonds — like rebuilding life"},
      {"name":"Vitamin E","percentage":5,"reason":"Antioxidant protection + skin nourishment"}
    ]
  }

stylist_script        JSONB
  {
    "opening": "You've chosen the colour of the sky before a storm clears. Let's work with that.",
    "mid_service": "You're halfway there — how are you feeling in the chair?",
    "closing": "Look at that. That's not just a new colour. That's the beginning of something.",
    "do_not_say": ["You look tired", "Are you stressed?", "What happened to your hair?"]
  }

mirror_monologue      TEXT
  "Priya arrived as Storm. She leaves as Phoenix. The transformation was always inside her — today we just let it show."

══ SOUL JOURNAL ENTRY ══
journal_date          DATE
archetype_of_day      VARCHAR(20)
private_life_note     TEXT          (written as if customer wrote it — empathetic, poetic)
look_created          TEXT          description of the look created for this emotion

══ METADATA ══
session_duration_mins INTEGER
customer_reaction     VARCHAR(50)   loved_it | neutral | didnt_engage
session_completed     BOOLEAN, default FALSE
created_at            TIMESTAMP
```

---

#### TABLE: mood_detections
Computer vision mood detection results. Captured at check-in, optional.

```
id                    UUID, PK
customer_id           UUID, FK → customer_profiles.id
booking_id            UUID, FK → bookings.id
captured_at           TIMESTAMP

detected_emotion      VARCHAR(50)   happy | sad | stressed | tired | neutral | excited | anxious
emotion_confidence    DECIMAL(4,2)  0.00 to 1.00
secondary_emotion     VARCHAR(50)
energy_level          VARCHAR(20)   low | medium | high
stress_indicators     JSONB         {facial_tension_score, eye_tiredness_score, brow_furrow_score}

recommended_archetype VARCHAR(20)   suggested SOULSKIN archetype from mood
service_adjustment    TEXT          LLM suggestion: "Consider offering extra scalp massage"
do_not_recommend      TEXT[]        ['loud_environment','chemical_treatments']

image_processed       BOOLEAN, default TRUE
image_stored          BOOLEAN, default FALSE  (face images NOT stored — privacy rule)
consent_given         BOOLEAN, default FALSE

created_at            TIMESTAMP
```

---

#### TABLE: digital_beauty_twins
The 3D digital model of a customer. Updated after every visit.

```
id                    UUID, PK
customer_id           UUID, UNIQUE, FK → customer_profiles.id

model_data_url        TEXT          S3 URL of 3D face model file (.glb or custom JSON)
texture_url           TEXT          S3 URL of face texture map
last_rebuilt_at       TIMESTAMP

skin_timeline         JSONB
  [
    {
      "date": "2026-01-15",
      "skin_score": 72,
      "acne_level": 2,
      "pigmentation_level": 3,
      "hydration": "normal",
      "snapshot_url": "https://s3.../snapshot_2026-01-15.jpg",
      "services_since_last": ["deep_cleansing_facial","vitamin_c_serum_treatment"]
    }
  ]

future_simulations    JSONB
  [
    {
      "simulation_id": "sim_001",
      "simulated_at": "2026-01-15",
      "weeks_ahead": 12,
      "predicted_state": {"skin_score":85,"acne_level":0,"pigmentation_level":1},
      "treatment_plan_assumed": ["monthly_facial","daily_spf","weekly_mask"],
      "simulation_image_url": "https://s3.../sim_001.jpg"
    }
  ]

hairstyle_tryons      JSONB
  [
    {
      "tryon_id": "tryon_001",
      "tried_at": "2026-01-15",
      "style_name": "Bob with curtain bangs",
      "color_applied": "warm copper",
      "tryon_image_url": "https://s3.../tryon_001.jpg",
      "customer_reacted": "loved"
    }
  ]

consent_given         BOOLEAN, default FALSE  (explicit consent required)
consent_date          TIMESTAMP
is_active             BOOLEAN, default TRUE

created_at, updated_at TIMESTAMP
```

---

#### TABLE: ar_mirror_sessions
Each AR Smart Mirror try-on session.

```
id                    UUID, PK
customer_id           UUID, FK → customer_profiles.id
booking_id            UUID, FK → bookings.id  (null if standalone)
location_id           UUID, FK → locations.id
initiated_by          ENUM: customer | stylist

session_type          ENUM: hairstyle | hair_color | makeup | skincare_preview | full_look

tryons                JSONB
  [
    {
      "sequence": 1,
      "type": "hair_color",
      "value": "warm_copper_balayage",
      "duration_seconds": 45,
      "customer_reaction": "positive",
      "saved": true
    }
  ]

final_selection       JSONB         what customer decided to actually do
climate_recommendations JSONB       weather-aware suggestions shown during session
  {
    "uv_index": 9.2,
    "humidity": 78,
    "recommendation": "High UV today — consider UV-protective gloss finish",
    "suggested_addons": ["UV_protection_serum","hydrating_mask"]
  }

session_duration_secs INTEGER
saved_images          TEXT[]        S3 URLs of try-on screenshots saved by customer
booking_created_after BOOLEAN, default FALSE  (did session lead to a booking?)

created_at            TIMESTAMP
```

---

#### TABLE: beauty_journey_plans
AI-generated 3-month or 6-month personalized beauty roadmap.

```
id                    UUID, PK
customer_id           UUID, FK → customer_profiles.id
generated_after_booking_id UUID, FK → bookings.id
plan_duration_weeks   INTEGER      12 (3 months) or 24 (6 months)
primary_goal          TEXT
generated_at          TIMESTAMP

milestones            JSONB
  [
    {
      "week": 1,
      "milestone": "Start recovery phase",
      "salon_visit": {
        "recommended_service": "Deep Protein Treatment",
        "service_id": "uuid",
        "estimated_cost": 1500,
        "why": "First step in damage repair journey"
      },
      "home_care": ["Apply coconut oil mask twice weekly", "Avoid heat styling"],
      "expected_outcome": "Reduced breakage by 20%"
    }
  ]

expected_outcomes     JSONB
  {
    "week_4":  "Visible reduction in hair fall, improved scalp condition",
    "week_8":  "Hair texture noticeably smoother, scalp balanced",
    "week_12": "Target achieved: 70% reduction in damage, natural shine restored"
  }

skin_projection       JSONB         predicted skin state at plan completion
estimated_total_cost  DECIMAL(10,2) sum of all recommended salon visits

ai_notes              TEXT          LLM-generated personalized narrative
whatsapp_sent         BOOLEAN, default FALSE
pdf_url               TEXT          S3 URL of generated PDF version

created_at            TIMESTAMP
```

---

#### TABLE: climate_recommendations
Real-time weather-based beauty advice (refreshed daily per city).

```
id                    UUID, PK
city                  VARCHAR(100), NOT NULL
date_for              DATE, NOT NULL
fetched_at            TIMESTAMP

temperature_celsius   DECIMAL(4,1)
humidity_pct          DECIMAL(4,1)
uv_index              DECIMAL(4,2)
aqi                   DECIMAL(6,2)
weather_condition     VARCHAR(100)  sunny | cloudy | rainy | windy | hazy

hair_recommendations  JSONB
  {
    "alerts": ["High humidity today — avoid keratin services", "Recommend anti-frizz serum"],
    "service_adjustments": ["Reduce blow-dry intensity — high humidity will cause frizz"],
    "home_care_tip": "Apply lightweight leave-in conditioner before stepping out"
  }

skin_recommendations  JSONB
  {
    "alerts": ["UV Index 9.2 — critical: recommend SPF 50 application"],
    "service_adjustments": ["Avoid chemical peels — high sun exposure today"],
    "home_care_tip": "Double SPF application. Reapply every 2 hours."
  }

general_advisory      TEXT
is_alert              BOOLEAN, default FALSE  (if UV > 8 or AQI > 200 — alert shown prominently)

UNIQUE constraint: (city, date_for)
created_at            TIMESTAMP
```

---

#### TABLE: smart_queue_entries
Real-time queue management for walk-ins.

```
id                    UUID, PK
location_id           UUID, FK → locations.id, NOT NULL
customer_id           UUID, FK → customer_profiles.id  (null if unknown walk-in)
customer_name         VARCHAR(200)  (for unregistered walk-ins)
customer_phone        VARCHAR(20)

service_id            UUID, FK → services.id
preferred_stylist_id  UUID, FK → staff_profiles.id  (null = any available)

status                ENUM: waiting | assigned | in_service | completed | left
position_in_queue     INTEGER
estimated_wait_mins   INTEGER      (AI-calculated based on current sessions)
actual_wait_mins      INTEGER      (filled on service start)

joined_queue_at       TIMESTAMP
assigned_at           TIMESTAMP
service_started_at    TIMESTAMP
service_completed_at  TIMESTAMP

notified_by_whatsapp  BOOLEAN, default FALSE
notification_sent_at  TIMESTAMP
notification_message  TEXT

walk_in_source        ENUM: in_person | whatsapp | app_checkin
notes                 TEXT

created_at, updated_at TIMESTAMP
```

---

#### TABLE: services
Master service catalog.

```
id                    UUID, PK
name                  VARCHAR(255), NOT NULL
category              VARCHAR(100)  hair | skin | nail | bridal | wellness | makeup
subcategory           VARCHAR(100)
description           TEXT
short_description     VARCHAR(255)
duration_minutes      INTEGER, NOT NULL
base_price            DECIMAL(10,2), NOT NULL
min_price             DECIMAL(10,2)
max_price             DECIMAL(10,2)
skill_required        ENUM: L1 | L2 | L3
is_chemical           BOOLEAN, default FALSE
is_active             BOOLEAN, default TRUE
sop_id                UUID, FK → sops.id
image_url             TEXT
ar_preview_available  BOOLEAN, default FALSE  (can be previewed in Smart Mirror)
tags                  TEXT[]  ['trending','bridal','premium','climate_adaptive']
created_at, updated_at TIMESTAMP
```

---

#### TABLE: sops
Step-by-step service delivery guides, multilingual.

```
id                    UUID, PK
service_id            UUID, FK → services.id
version               VARCHAR(20), default '1.0'
title                 VARCHAR(255)
is_current            BOOLEAN, default TRUE

steps                 JSONB, NOT NULL
  [
    {
      "step_number": 1,
      "title": {"en":"Consultation","ta":"ஆலோசனை","hi":"परामर्श","te":"సంప్రదింపు","kn":"ಸಮಾಲೋಚನೆ"},
      "instructions": {"en":"...","ta":"...","hi":"...","te":"...","kn":"..."},
      "duration_minutes": 5,
      "products_required": ["clarifying_shampoo"],
      "critical": true,
      "warning": "Check allergy profile before this step",
      "image_url": "...",
      "video_url": "...",
      "timer_required": false,
      "timer_seconds": null,
      "soulskin_note": "For Storm archetype: speak softly, do not rush this step"
    }
  ]

soulskin_overlays     JSONB
  (archetype-specific guidance overlaid on steps)
  {
    "phoenix": {"overall_note":"Bold and decisive — client wants transformation speed"},
    "storm":   {"overall_note":"Slow and grounding — take extra time on scalp massage"},
    "moon":    {"overall_note":"Silent or soft music — minimal conversation"},
    "bloom":   {"overall_note":"Celebrate with client — this is a happy occasion"},
    "river":   {"overall_note":"Transition energy — acknowledge the change they're in"}
  }

products_required     TEXT[]
chemicals_involved    BOOLEAN, default FALSE
chemical_ratios       JSONB  {"developer":1,"color_cream":1.5}
total_duration_minutes INTEGER
created_by            UUID, FK → users.id
created_at, updated_at TIMESTAMP
```

---

#### TABLE: bookings

```
id                    UUID, PK
booking_number        VARCHAR(20), UNIQUE  (BK-2026-000001)
customer_id           UUID, FK → customer_profiles.id
location_id           UUID, FK → locations.id
stylist_id            UUID, FK → staff_profiles.id
service_id            UUID, FK → services.id
soulskin_session_id   UUID, FK → soulskin_sessions.id  (null if no soul reading)
ar_session_id         UUID, FK → ar_mirror_sessions.id (null if no try-on)
queue_entry_id        UUID, FK → smart_queue_entries.id (null if appointment)

status                ENUM: pending | confirmed | checked_in | in_progress |
                             completed | cancelled | no_show | rescheduled
scheduled_at          TIMESTAMP, NOT NULL
actual_start_at       TIMESTAMP
actual_end_at         TIMESTAMP
duration_variance_minutes INTEGER

base_price            DECIMAL(10,2)
discount_percent      DECIMAL(5,2), default 0
discount_reason       VARCHAR(255)
final_price           DECIMAL(10,2)
payment_status        ENUM: pending | paid | partial | refunded
payment_method        ENUM: cash | card | upi | wallet

source                ENUM: walk_in | app | whatsapp | phone | website | queue
notes                 TEXT
internal_notes        TEXT
add_on_services       UUID[]

cancellation_reason   TEXT
cancelled_at          TIMESTAMP
cancelled_by          UUID, FK → users.id
rescheduled_from      UUID, FK → bookings.id

reminder_sent_24h     BOOLEAN, default FALSE
reminder_sent_2h      BOOLEAN, default FALSE
followup_sent         BOOLEAN, default FALSE
journey_plan_generated BOOLEAN, default FALSE

created_at, updated_at TIMESTAMP
```

---

#### TABLE: service_sessions
Live session during service delivery. Offline-capable data model.

```
id                    UUID, PK
booking_id            UUID, UNIQUE, FK → bookings.id
sop_id                UUID, FK → sops.id
sop_version           VARCHAR(20)
soulskin_session_id   UUID, FK → soulskin_sessions.id

status                ENUM: not_started | active | paused | completed | abandoned

steps_total           INTEGER
steps_completed       INTEGER[], default '{}'
current_step          INTEGER, default 1
started_at            TIMESTAMP
paused_at             TIMESTAMP
resumed_at            TIMESTAMP
completed_at          TIMESTAMP

products_used         JSONB
chemical_ratios_used  JSONB
processing_start_time TIMESTAMP
processing_end_time   TIMESTAMP

deviations            JSONB  [{step, reason, logged_at}]
ai_coaching_prompts   JSONB  (pre-generated per step for this customer)
soulskin_active       BOOLEAN, default FALSE
archetype_applied     VARCHAR(20)

before_image_url      TEXT
after_image_url       TEXT

quality_score         DECIMAL(4,2)
sop_compliance_pct    DECIMAL(4,2)
timing_compliance     DECIMAL(4,2)

stylist_notes         TEXT

-- OFFLINE SYNC FIELDS
last_synced_at        TIMESTAMP
has_offline_changes   BOOLEAN, default FALSE
offline_actions_queue JSONB  (queued actions when offline)

created_at, updated_at TIMESTAMP
```

---

#### TABLE: quality_assessments

```
id                    UUID, PK
booking_id            UUID, UNIQUE, FK → bookings.id
session_id            UUID, FK → service_sessions.id
stylist_id            UUID, FK → staff_profiles.id
location_id           UUID, FK → locations.id
service_id            UUID, FK → services.id

sop_compliance_score  DECIMAL(4,2)   0-100
timing_score          DECIMAL(4,2)   0-100
customer_rating       INTEGER        1-5 stars
manager_rating        INTEGER        1-5 stars
overall_score         DECIMAL(4,2)   weighted composite

before_image_url      TEXT
after_image_url       TEXT
ai_analysis_result    JSONB

ai_feedback           TEXT           constructive, stylist-specific
ai_feedback_generated_at TIMESTAMP

is_flagged            BOOLEAN, default FALSE
flag_reason           TEXT
reviewed_by_manager   BOOLEAN, default FALSE
manager_review_note   TEXT

soulskin_alignment_score DECIMAL(4,2) did the service match the archetype plan?

created_at            TIMESTAMP
```

---

#### TABLE: skill_assessments

```
id                    UUID, PK
staff_id              UUID, FK → staff_profiles.id
assessed_by           UUID, FK → users.id
assessment_type       ENUM: self | manager | ai | peer | external_trainer
service_category      VARCHAR(100)
skill_area            VARCHAR(100)
current_level         ENUM: L1 | L2 | L3
score                 DECIMAL(4,2)
rubric_scores         JSONB  {technique, speed, consultation, product_knowledge, customer_handling}
l2_gap_items          TEXT[]
l3_gap_items          TEXT[]
recommended_training  TEXT[]
soulskin_certified    BOOLEAN  (if assessment includes emotional intelligence module)
assessment_notes      TEXT
created_at            TIMESTAMP
```

---

#### TABLE: training_records

```
id                    UUID, PK
staff_id              UUID, FK → staff_profiles.id
training_name         VARCHAR(255)
training_type         ENUM: classroom | online | on_job | external_workshop
service_category      VARCHAR(100)
provider              VARCHAR(255)
trainer_name          VARCHAR(255)
start_date            DATE
end_date              DATE
hours_completed       DECIMAL(5,1)
cost_to_company       DECIMAL(10,2)
passed                BOOLEAN
score                 DECIMAL(4,2)
certificate_url       TEXT
includes_soulskin     BOOLEAN, default FALSE

-- ROI tracking (BI engine updates these)
revenue_before        DECIMAL(12,2)
revenue_after         DECIMAL(12,2)
quality_score_before  DECIMAL(4,2)
quality_score_after   DECIMAL(4,2)
roi_calculated_at     TIMESTAMP

notes                 TEXT
created_at, updated_at TIMESTAMP
```

---

#### TABLE: trend_signals

```
id                    UUID, PK
trend_name            VARCHAR(255), NOT NULL
slug                  VARCHAR(255), UNIQUE
description           TEXT
service_category      VARCHAR(100)
applicable_regions    TEXT[]
applicable_cities     TEXT[]

overall_signal_strength DECIMAL(4,2)
social_media_score    DECIMAL(4,2)
search_trend_score    DECIMAL(4,2)
booking_demand_score  DECIMAL(4,2)
influencer_score      DECIMAL(4,2)
celebrity_trigger     TEXT         (e.g., "Deepika Padukone debuted copper highlights")

trajectory            ENUM: emerging | growing | peak | declining
longevity_label       ENUM: fad | trend | movement
predicted_peak_date   DATE
confidence_level      DECIMAL(3,2)

inventory_actions     JSONB
training_actions      JSONB
marketing_actions     JSONB

cover_image_url       TEXT
example_image_urls    TEXT[]
source_urls           TEXT[]

climate_correlation   JSONB  (does this trend correlate with specific weather?)
  {"season":"monsoon","climate_type":"tropical","notes":"Glass skin surges in humidity"}

detected_at           TIMESTAMP
expires_at            TIMESTAMP
is_active             BOOLEAN, default TRUE
created_at            TIMESTAMP
```

---

#### TABLE: customer_feedback

```
id                    UUID, PK
booking_id            UUID, FK → bookings.id
customer_id           UUID, FK → customer_profiles.id
stylist_id            UUID, FK → staff_profiles.id
location_id           UUID, FK → locations.id
service_id            UUID, FK → services.id
soulskin_session_id   UUID, FK → soulskin_sessions.id

overall_rating        INTEGER, NOT NULL  1-5
service_rating        INTEGER
stylist_rating        INTEGER
ambiance_rating       INTEGER
value_for_money       INTEGER
soulskin_experience_rating INTEGER  (did they love the soul reading?)
would_recommend       BOOLEAN

comment               TEXT
tags                  TEXT[]   NLP-extracted
sentiment             ENUM: positive | neutral | negative
sentiment_score       DECIMAL(4,2)

source                ENUM: app | whatsapp | google | sms | in_person
is_verified           BOOLEAN, default FALSE
is_responded          BOOLEAN, default FALSE
response_text         TEXT
responded_at          TIMESTAMP
responded_by          UUID, FK → users.id

created_at            TIMESTAMP
```

---

#### TABLE: homecare_plans

```
id                    UUID, PK
customer_id           UUID, FK → customer_profiles.id
booking_id            UUID, FK → bookings.id
soulskin_archetype    VARCHAR(20)  (archetype at time of this plan)
generated_at          TIMESTAMP
plan_duration_weeks   INTEGER

hair_routine          JSONB  {daily, weekly, monthly}
skin_routine          JSONB  {daily, weekly, monthly}
climate_adjustments   JSONB  (weather-specific additions)
archetype_rituals     JSONB  (SOULSKIN-specific self-care for their archetype)
  {
    "phoenix": "Begin each morning with 2 minutes of scalp stimulation massage to activate growth energy",
    "storm": "End each evening with lavender oil application on temples — grounding ritual"
  }

product_recommendations JSONB  [{product_name, usage, reason, estimated_price}]
dos                   TEXT[]
donts                 TEXT[]
next_visit_recommendation VARCHAR(255)
next_visit_suggested_date DATE
ai_notes              TEXT
whatsapp_sent         BOOLEAN, default FALSE
pdf_url               TEXT

created_at            TIMESTAMP
```

---

#### TABLE: notifications

```
id                    UUID, PK
user_id               UUID, FK → users.id
notification_type     VARCHAR(100)  booking_reminder | trend_alert | quality_flag |
                                    attrition_risk | soulskin_journal | journey_milestone |
                                    climate_alert | queue_update
title                 VARCHAR(255)
body                  TEXT
data                  JSONB
channel               ENUM: push | whatsapp | sms | email | in_app
priority              ENUM: low | normal | high | urgent
is_read               BOOLEAN, default FALSE
sent_at               TIMESTAMP
read_at               TIMESTAMP
failed_at             TIMESTAMP
failure_reason        TEXT
created_at            TIMESTAMP
```

---

## PART 4: FULL API STRUCTURE

### 4.1 Base Config
```
Base URL:     /api/v1/
Auth Header:  Authorization: Bearer <access_token>
Refresh:      httpOnly cookie: refresh_token
Response:     { "success": bool, "data": any, "message": str, "errors": [] }
Pagination:   ?page=1&per_page=20
Filtering:    ?location_id=&date_from=&status=
```

### 4.2 All Endpoint Groups

#### AUTH
```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/forgot-password
POST   /auth/reset-password
POST   /auth/verify-email
POST   /auth/send-otp
POST   /auth/verify-otp
GET    /auth/me
PATCH  /auth/me
PATCH  /auth/me/password
POST   /auth/me/avatar
POST   /auth/me/push-token         (register PWA push notification token)
```

#### LOCATIONS
```
GET    /locations
POST   /locations                  (SUPER only)
GET    /locations/{id}
PATCH  /locations/{id}
DELETE /locations/{id}             (soft delete, SUPER only)
GET    /locations/{id}/staff
GET    /locations/{id}/analytics
GET    /locations/{id}/quality
GET    /locations/{id}/trends
GET    /locations/{id}/queue       (live queue state)
GET    /locations/{id}/climate     (today's climate recommendations)
GET    /locations/map
```

#### STAFF
```
GET    /staff
POST   /staff
GET    /staff/{id}
PATCH  /staff/{id}
DELETE /staff/{id}
GET    /staff/{id}/schedule
GET    /staff/{id}/bookings
GET    /staff/{id}/quality-scores
GET    /staff/{id}/skills
POST   /staff/{id}/skills
GET    /staff/{id}/training
POST   /staff/{id}/training
GET    /staff/{id}/attrition-risk
GET    /staff/{id}/performance
GET    /staff/{id}/soulskin-stats  (how often they use SOULSKIN, archetype breakdown)
GET    /staff/availability
```

#### CUSTOMERS (BEAUTY PASSPORT)
```
GET    /customers
POST   /customers
GET    /customers/{id}
PATCH  /customers/{id}
GET    /customers/{id}/history
GET    /customers/{id}/recommendations
GET    /customers/{id}/homecare
GET    /customers/{id}/timeline
GET    /customers/{id}/before-afters
GET    /customers/{id}/soul-journal          (all SOULSKIN entries)
GET    /customers/{id}/digital-twin          (Digital Beauty Twin data)
GET    /customers/{id}/journey-plan          (current beauty journey plan)
GET    /customers/{id}/ar-tryons             (AR Smart Mirror history)
POST   /customers/{id}/scan                  (submit image for AI analysis)
POST   /customers/{id}/lifestyle             (update lifestyle data)
POST   /customers/{id}/goal                  (set beauty goal)
DELETE /customers/{id}                       (DPDP right to erasure)
GET    /customers/search
```

#### BOOKINGS
```
GET    /bookings
POST   /bookings
GET    /bookings/{id}
PATCH  /bookings/{id}
DELETE /bookings/{id}
POST   /bookings/{id}/check-in
POST   /bookings/{id}/start
POST   /bookings/{id}/complete
POST   /bookings/{id}/no-show
GET    /bookings/slots
GET    /bookings/today
GET    /bookings/upcoming
GET    /bookings/calendar
```

#### SERVICE SESSIONS (LIVE AI GUIDANCE)
```
GET    /sessions/{booking_id}
POST   /sessions/{booking_id}/start
POST   /sessions/{booking_id}/step/{n}       (mark step complete)
POST   /sessions/{booking_id}/deviation      (log SOP deviation)
POST   /sessions/{booking_id}/pause
POST   /sessions/{booking_id}/resume
POST   /sessions/{booking_id}/complete
GET    /sessions/{booking_id}/guidance       (AI guidance for current step + archetype overlay)
POST   /sessions/{booking_id}/before-photo
POST   /sessions/{booking_id}/after-photo
GET    /sessions/{booking_id}/timer
POST   /sessions/{booking_id}/timer/start
POST   /sessions/{booking_id}/sync           (offline sync — batch upload queued actions)
```

#### SOULSKIN ENGINE
```
POST   /soulskin/sessions                    (start soul reading)
GET    /soulskin/sessions/{id}               (get full session)
PATCH  /soulskin/sessions/{id}               (update with questions answered)
POST   /soulskin/sessions/{id}/generate      (trigger LLM generation of full experience)
GET    /soulskin/sessions/{id}/script        (stylist script for this session)
GET    /soulskin/sessions/{id}/formula       (custom formula for this session)
GET    /soulskin/journal/{customer_id}       (all soul journal entries)
GET    /soulskin/archetypes                  (list of archetypes with descriptions)
GET    /soulskin/stats/{location_id}         (archetype distribution at location)
```

#### MOOD DETECTION
```
POST   /mood/detect                          (submit image for mood analysis)
GET    /mood/{booking_id}                    (mood detection result for booking)
GET    /mood/history/{customer_id}           (mood history — customer consent required)
```

#### DIGITAL BEAUTY TWIN
```
GET    /twin/{customer_id}                   (get twin data)
POST   /twin/{customer_id}/rebuild           (trigger 3D model rebuild from latest scan)
POST   /twin/{customer_id}/simulate          (trigger future skin simulation)
GET    /twin/{customer_id}/simulations       (all simulations)
POST   /twin/{customer_id}/hairstyle-tryon   (apply hairstyle to twin)
```

#### AR SMART MIRROR
```
POST   /mirror/sessions                      (start mirror session)
GET    /mirror/sessions/{id}
POST   /mirror/sessions/{id}/tryon           (log a try-on event)
POST   /mirror/sessions/{id}/save            (save try-on image)
POST   /mirror/sessions/{id}/complete
GET    /mirror/styles                        (available hairstyles for AR)
GET    /mirror/colors                        (available color options)
GET    /mirror/climate-suggestions           (weather-based suggestions for today)
```

#### BEAUTY JOURNEY PLANNER
```
POST   /journey/generate/{customer_id}       (generate new 3/6 month plan)
GET    /journey/{customer_id}                (current active plan)
GET    /journey/{customer_id}/history        (all past plans)
GET    /journey/{customer_id}/progress       (progress vs. plan milestones)
POST   /journey/{id}/send-whatsapp           (send plan via WhatsApp)
POST   /journey/{id}/generate-pdf            (generate PDF version)
```

#### CLIMATE RECOMMENDATIONS
```
GET    /climate/{city}                       (today's climate recommendations)
GET    /climate/{city}/forecast              (7-day beauty forecast)
POST   /climate/sync                         (admin: force refresh all city data)
```

#### SMART QUEUE
```
GET    /queue/{location_id}                  (current queue state — live)
POST   /queue/{location_id}/join             (customer joins queue)
PATCH  /queue/{location_id}/{entry_id}       (update entry)
POST   /queue/{location_id}/{entry_id}/assign (assign to stylist)
POST   /queue/{location_id}/{entry_id}/notify (send WhatsApp notification)
GET    /queue/{location_id}/wait-estimate    (AI wait time estimate)
DELETE /queue/{location_id}/{entry_id}       (customer left queue)
```

#### SOPs & SERVICES
```
GET    /services
POST   /services
GET    /services/{id}
PATCH  /services/{id}
GET    /services/{id}/sop
GET    /sops
POST   /sops
GET    /sops/{id}
PATCH  /sops/{id}
POST   /sops/{id}/new-version
GET    /sops/{id}/versions
```

#### TRENDS
```
GET    /trends
GET    /trends/{id}
GET    /trends/alerts
GET    /trends/forecast
GET    /trends/inventory
GET    /trends/training
GET    /trends/calendar
```

#### ANALYTICS & BI
```
GET    /analytics/overview
GET    /analytics/revenue
GET    /analytics/quality
GET    /analytics/staff
GET    /analytics/customers
GET    /analytics/training-roi
GET    /analytics/skill-gap
GET    /analytics/attrition
GET    /analytics/compare
GET    /analytics/forecast
GET    /analytics/soulskin               (archetype distribution, soul session impact on ratings)
POST   /analytics/export
```

#### FEEDBACK, NOTIFICATIONS, HOMECARE
```
GET/POST /feedback
GET      /feedback/summary
GET      /feedback/sentiment
POST     /feedback/{id}/respond

GET      /notifications
PATCH    /notifications/{id}/read
PATCH    /notifications/read-all
GET      /notifications/unread-count

GET      /homecare/{customer_id}
POST     /homecare/generate
GET      /homecare/{customer_id}/history
POST     /homecare/{id}/send-whatsapp
```

---

## PART 5: FRONTEND — ALL PAGES & SCREENS

### DESIGN LANGUAGE

```
Theme:           Luxury dark. Deep beauty. Not generic SaaS.
Background:      #0A0A0F (near-black with blue undertone)
Surface:         #111116 / #16161E / #1C1C26 (layered depth)
Border:          #252530 / #3A3A4A
Text Primary:    #F0EEF8 (slightly warm white)
Text Secondary:  #9B99B0
Text Muted:      #5C5A70
Accent Gold:     #C9A96E (Naturals premium feel)
Accent Teal:     #2A9D8F (intelligence, calm)
Accent Rose:     #E76F6F (alerts, emotion)
Accent Violet:   #9B7FD4 (SOULSKIN — spiritual, deep)
Success:         #52B788
Warning:         #F4A261
Error:           #E76F6F

Typography:
  Display:       "Playfair Display" — emotional, elegant, beauty-native
  Body:          "DM Sans" — clean, readable, modern
  Mono:          "JetBrains Mono" — data values, codes

SOULSKIN Module specific:
  Background overlay:  Deep violet-black gradient (#0D0A1A → #0A0A0F)
  Archetype colors:
    Phoenix: #E8611A (fire orange)
    River:   #4A9FD4 (water blue)
    Moon:    #7B68C8 (deep violet)
    Bloom:   #E8A87C (warm peach)
    Storm:   #6B8FA6 (grey-blue steel)

Animations:
  Page transitions:   Framer Motion fade + Y-slide 200ms
  List reveals:       Staggered 50ms delay per item
  Charts:             Animate on mount
  SOULSKIN reveal:    Slow dramatic fade-in, letter-by-letter for soul reading text
  AR Mirror:          WebGL canvas, 60fps MediaPipe real-time overlay
  Digital Twin:       Three.js renderer, orbit controls
  Loading:            Skeleton screens (never spinners)
  PWA install prompt: Slide up from bottom, beauty brand styled

Sidebar:         Fixed left, 240px expanded / 60px icon-only collapsed
                 Role-specific items only
                 Dark surface (#111116) with gold border-right
                 Bottom: user avatar + role badge + settings + logout

Mobile / PWA:    Bottom tab navigation (5 icons)
                 Stylist session page: full-screen, distraction-free
                 All inputs optimized for touch (large tap targets, 48px min)
```

---

### 5.1 PUBLIC PAGES

---
#### LANDING PAGE  |  `/`

Full viewport hero with Three.js animated canvas.
Purpose: Judge-facing demo, franchise inquiries, customer discovery.

**SECTION 1 — HERO**
Three.js canvas: Abstract particles slowly forming a woman's face with a neural network overlay on the left, and floating salon analytics data on the right. They merge center into AURA logo. Continuous, gentle, 60fps. On mobile: particle animation replaced with static gradient (performance).
- Headline: "Every Salon Visit. Every Soul. Understood." — Playfair Display, letter-by-letter animation
- Sub: "AURA transforms Naturals into an AI-powered beauty ecosystem across 750+ locations"
- CTAs: "Explore Platform" (scroll) | "Get Started" (/register)
- Trust strip: Naturals logo + StartupTN logo + "Hackathon 2026"

**SECTION 2 — THREE INTELLIGENCE LAYERS**
Three large cards in a row (or vertical on mobile):
- Physical Intelligence → face icon → "AI reads your hair, skin, and body"
- Emotional Intelligence → soul icon (SOULSKIN) → "AI reads what you're going through in life"
- Predictive Intelligence → trend icon → "AI reads what tomorrow's beauty demand will be"
Animated: each card flips on scroll to reveal "How it works" detail.

**SECTION 3 — STATS**
Animated counters on scroll: 750+ Salons | 8 AI Modules | 6 User Roles | 0 Prototypes

**SECTION 4 — THE SOULSKIN REVEAL**
This section must feel magical. Dark background, violet accent color.
- Title: "Introducing SOULSKIN — The World's First Emotion-to-Beauty Intelligence System"
- Sub: "People don't visit salons to change their hair. They visit when something in their life is changing."
- 3 input fields shown in animation:
  - "The song that describes your life right now..."
  - "The colour that matches your mood today..."
  - "The one word you want to FEEL when you leave..."
- Below: archetype grid animates in — Phoenix | River | Moon | Bloom | Storm — each with color
- CTA: "See Your Reading" → /register

**SECTION 5 — 8 MODULES BENTO GRID**
Asymmetric bento grid. 8 cards total.
Large cards: Beauty Passport | SOULSKIN Engine
Medium cards: AR Smart Mirror | Digital Beauty Twin | AI Stylist Assistant
Small cards: Trend Intelligence | Staff Intelligence | BI Dashboard
Each card: icon + module name + one-sentence description. Hover: expands, shows mini mockup screenshot.

**SECTION 6 — AR SMART MIRROR DEMO**
Split section:
- Left: animated mockup of Smart Mirror showing AR try-on on a face
- Right: headline "Try It Before You Commit" + 3 bullet features + CTA

**SECTION 7 — ROLE SHOWCASE**
Tab strip: Customer | Stylist | Manager | Franchise Owner
Each tab shows device mockup + 3 key benefits + short quote

**SECTION 8 — TECH CREDIBILITY**
Architecture diagram (SVG) + tech stack logos + DPDP Act badge + ACID badge + PWA badge

**SECTION 9 — CTA FOOTER**
"Ready to transform Naturals?"
Two buttons: Demo Request | Sign Up

---
#### LOGIN  |  `/login`
Two column. Left: AURA dark brand panel with animated tagline rotation. Right: login form.
Fields: Email, Password (show/hide). Remember me. Forgot password link.
After login: role-based redirect.

---
#### REGISTER (CUSTOMER)  |  `/register`
3-step form with progress indicator.
Step 1: Name, Email, Phone, Password, Language preference
Step 2: City, Preferred Naturals location, How did you hear
Step 3: OTP verification
On complete: redirect to /app/onboarding (Beauty Passport setup wizard)

---

### 5.2 CUSTOMER PORTAL  |  `/app/*`
Mobile-first PWA. Bottom tab navigation.
PWA prompt: shown on second visit "Add AURA to your home screen for instant beauty intelligence"

**Bottom Tabs**: 🏠 Home | 📖 Passport | 🪞 Mirror | 📅 Bookings | 💆 Journey

---
#### CUSTOMER HOME  |  `/app/dashboard`
- Greeting with first name and time of day
- Weather card: "Chennai today — UV 9.2 | Humidity 78% | AQI 142" with climate beauty alert if triggered
- Beauty Score ring (0-100 composite score)
- "Your Vibe Today" section: small SOULSKIN teaser — "How are you feeling?" → taps to open SOULSKIN pre-reading
- AI Recommendations: 3 cards (service + reason + price + Book button)
- Upcoming Booking: if any — date, stylist, service, location
- Recent Journey Milestone: latest milestone from beauty journey plan
- Trending near you: 1 trend card from trend_signals relevant to their city
- Quick Book FAB button (floating action button, bottom right)

---
#### BEAUTY PASSPORT  |  `/app/passport`
Premium digital passport design. Feels like a luxury document.

**Header**: AURA logo + "Beauty Passport" watermark text. Customer photo. Passport completeness ring.

**Tabs**: Overview | Hair | Skin | Lifestyle | Safety | Soul Profile | History

Tab — Overview:
- Beauty score ring (large)
- Last scan date and thumbnail. "Rescan" button opens camera.
- Top 3 insights from latest scan
- Quick stats: Total visits, Lifetime value tier (Bronze/Silver/Gold), Preferred stylist

Tab — Hair:
- All hair diagnostic cards (type, texture, porosity, density, scalp, damage)
- Visual: color swatch of current hair color
- Chemical treatment timeline (horizontal scroll)
- Recommendations card: "Your hair needs..."

Tab — Skin:
- Skin type, tone, undertone displayed
- Concern chips (acne, pigmentation, etc.) with severity bars
- Latest skin score + trend arrow (improving/worsening)
- Climate-matched advice card (today's UV/humidity context)

Tab — Lifestyle:
- Live weather widget for their city
- Lifestyle inputs (editable): sleep, hydration, stress, diet
- "Your environment is affecting your beauty" — dynamic insight based on AQI + UV

Tab — Safety:
- Allergen list with warning icons (RED for PPD if present)
- Product sensitivities
- Patch test record
- Important: if any allergy → red banner at top of tab

Tab — Soul Profile (SOULSKIN history):
- Current dominant archetype with description and archetype color
- Archetype history: mini timeline showing archetype per visit
- Emotional sensitivity level
- "Your beauty is deeply personal. These readings help us serve your whole self."

Tab — History:
- Timeline of all past services (newest first)
- Each: date, service, stylist, location, before/after thumbs, rating, quality score

---
#### AR SMART MIRROR  |  `/app/mirror`
The most visually impressive page. Full-screen camera experience.

**States**:
1. Permission Request: elegant modal asking for camera access
2. Face Detection: camera live feed with MediaPipe face mesh overlay. Status: "Position your face in the frame"
3. Active Try-On: face mesh locked. Category tabs at top.
4. Review: selected try-on shown, before/after toggle, save/share

**Category Tabs (when face detected)**:
- 💇 Hairstyle: scroll-select from style thumbnails. AR renders instantly on face.
- 🎨 Hair Color: color palette grid. Click to apply. Real-time color overlay on hair region.
- 💄 Makeup: filter-style options
- ✨ Skincare Result: show predicted "after" of recommended facial treatment

**Climate Suggestion Banner**:
Appears at bottom: "Today's UV: 9.2 in Chennai — We recommend UV-protective gloss finish 🌞"
Recommendation adapts to real-time climate_recommendations data.

**Interaction**:
- Long-press on any try-on: save to gallery
- "Book This Look" button: auto-populates booking with matched service
- "Share" button: save image + share to WhatsApp (with consent)

**Save History**: grid of all saved try-ons from ar_mirror_sessions.hairstyle_tryons

---
#### BOOKINGS  |  `/app/bookings`

**Upcoming**: list of confirmed bookings. Each: service, stylist, date/time, location. Reschedule + Cancel.
**Past**: history list with rating prompt on recently completed bookings.
**Book New** `/app/book`:
Step 1: Location (map view + list. "Near me" uses GPS)
Step 2: Service category + service selection. AI Recommended badge.
Step 3: Stylist selection + date + time slots
Step 4: Confirm. Climate recommendation shown for the selected date.
Booking confirmation → WhatsApp notification auto-sent.

---
#### BEAUTY JOURNEY  |  `/app/journey`
6-month roadmap visual.

**Header**: Goal statement + end date + progress ring

**Timeline View** (vertical scroll):
Each milestone is a card: week number, what to do at salon, what to do at home, expected outcome.
Current week: highlighted with gold border, pulsing indicator.
Completed milestones: checkmark, before/after micro-thumbnail.
Upcoming: slightly dimmed, "Unlock in X weeks"

**Tabs**: Salon Plan | Home Care | Products | Progress

Tab — Progress:
- Skin score over time line chart
- Hair damage level trend chart
- Before/After photos at key milestones (side by side)
- "You are X% toward your goal"

"Generate New Journey Plan" CTA (after each completed booking).

---
#### SOULSKIN ENTRY (accessed from Home or pre-booking)  |  `/app/soulskin`
Dark mode forced. Violet accent. This page feels sacred, intimate.

**State 1 — Intro**:
Fade-in text: "Before we touch your hair, we want to understand you."
"Three questions. Sixty seconds. An experience designed entirely for your soul today."
"Begin" button — gentle, not urgent.

**State 2 — Three Questions** (one per screen, fullscreen focus):
Q1: Large text "What song describes your life right now?" — free text input, no suggestions, no pressure.
Q2: Colour picker — not a dropdown, actual color swatches on a dark canvas, tap to select. Can also type colour name.
Q3: "One word you want to FEEL when you leave." — single word text input.
Progress dots at bottom (1/3, 2/3, 3/3).

**State 3 — Soul Reading** (LLM generating, dramatic loading):
Loading screen: slow pulsing SOULSKIN logo + "Reading your soul..." text. 3-4 seconds.
NOT a spinner. A meaningful pause.

**State 4 — Reveal** (the most beautiful screen in the entire app):
Archetype revealed with animation:
- Screen fades to archetype color (e.g., fire orange for Phoenix)
- Archetype symbol appears (large, centered, animated in)
- Name appears: "YOU ARE — 🔥 PHOENIX"
- Then soul reading text appears, line by line, slow fade:
  Line 1: "You are standing at the edge of something ending..."
  Line 2: "You are not afraid of the fire..."
  Line 3: "You are ready to become what you always were."
- Below: archetype reason paragraph

**State 5 — Experience Preview** (show what's been designed for them):
Cards reveal one by one (each with a slow fade):
- Service Protocol card (what treatment + why)
- Colour Direction card (colour story + symbolism)
- Sensory Environment card (scents + music preview with Spotify/YouTube links)
- Custom Formula card (5 ingredients)

**State 6 — Journal Entry**:
Shows the soul journal entry for this session.
"Save to Journal" + "Share with Stylist" buttons.

---

### 5.3 STYLIST PORTAL  |  `/stylist/*`
PWA, mobile-optimized, offline-capable.

**Bottom Tabs**: 📅 Today | 🪄 Session | 👤 Customers | 📈 My Growth | 🎓 Training

---
#### STYLIST TODAY  |  `/stylist/dashboard`
**Top bar**: Date, location, availability toggle, SOULSKIN certified badge (if applicable).

**Live Session Banner**: If session active → "Session in progress — Tap to return" (always visible)

**Today's Queue**: Timeline of bookings. Each card:
- Time, customer name, service, duration
- Status chip: Upcoming (grey) | Next Up (gold pulse) | In Progress (teal) | Done (green)
- Allergy warning badge if customer has known allergies
- SOULSKIN archetype badge if soul reading has been done (Phoenix/River/Moon/Bloom/Storm)

**Next Up Card** (top, prominent):
- Customer name, photo, service
- "View Passport" button → opens customer view
- "Start SOULSKIN" button → opens SOULSKIN flow for this customer
- "Start Service" button (activates 15 min before scheduled time)

**My Today Stats**: Revenue generated | Services done | Average rating | Quality score today

---
#### LIVE SESSION  |  `/stylist/session/{booking_id}`
THE MOST CRITICAL PAGE. Offline-capable. Full-screen immersive.

**Layout**: Top fixed header. Scrollable main area. Bottom fixed action bar.

**Header** (fixed top):
- Customer name | Service name
- Session timer (counting up)
- Benchmark indicator: "On time" (green) / "Running late: +8 min" (amber) / "Overdue" (red)
- Step counter: "Step 4 / 12"
- SOULSKIN archetype badge (if active): colored dot + archetype name

**SOULSKIN BANNER** (if soul reading done):
Collapsible banner below header, archetype color:
- Archetype icon + name
- One-line reminder from stylist script: "Opening: [opening line]"
- Tap to expand full stylist script (all 4 lines + do-not-say)

**Allergy Alert** (if applicable):
Full-width RED banner: "⚠️ PPD Allergy — avoid tinting products"

**Main Content — Current Step Card**:
Large card, full attention:
- Step number (large, Playfair Display)
- Step title (in stylist's preferred language)
- Instructions (clear, numbered sub-steps)
- Products needed: pill chips for each product
- If chemical step: chemical ratios displayed LARGE: "Developer 1 : Color 1.5"
- If timer step: countdown timer card (large digits, progress ring, alarm sound at 2 min remaining)
- Image (if available): collapsible
- Video (if available): inline player

**AI Coaching Bubble**:
Collapsible bottom-right bubble: "💡 AI Tip"
On tap: expands to show customer-specific coaching for THIS step:
"Priya has HIGH POROSITY — use extra protein serum at this step and extend processing by 5 min"
This is pre-generated by LLM on session start, so it works offline.

**SOULSKIN Step Overlay**:
If SOULSKIN session active, small italic note under instructions:
"Storm archetype: speak less, move slowly — she needs grounding not stimulation right now"

**Action Bar** (fixed bottom):
- "◀ Previous" (small, grey — review only, cannot un-complete)
- "✓ Mark Complete" (large teal, full-width feel)
- "⚠ Log Deviation" (small, amber link)

**Photo Capture Prompts**:
On Step 1: "📸 Capture Before Photo" button appears in main content
On Final Step: "📸 Capture After Photo" button appears

**Session Complete Modal** (when last step marked done):
- Summary: X/Y steps completed, time: Z min (vs benchmark)
- Quality score preview (calculated)
- "Submit & Complete Session" button
- On submit: session complete, quality assessment created, feedback request queued for WhatsApp

**Offline Indicator**:
If offline: amber banner at top: "Offline Mode — All actions will sync when connected"
Session still works 100% offline. Actions queued in IndexedDB.
When online restored: auto-sync with indicator "Syncing 3 actions..."

---
#### CUSTOMER VIEW (Stylist's view)  |  `/stylist/customers/{id}`
Read-focused. Can add notes.

- Customer photo + name + beauty score ring
- ALLERGY ALERTS in red at top if any
- Hair summary: quick diagnostic tiles
- Skin summary: quick diagnostic tiles
- Archetype history: last 5 archetypes with dates
- Service history: last 5 visits with mini cards
- Notes section: chronological stylist notes. "Add Note" → rich text input.
- Current SOULSKIN session preview (if done today)

---
#### MY PERFORMANCE  |  `/stylist/performance`
Period selector: Week / Month / 3 Months / All Time

**KPI Row**: Total services | Avg quality score | Avg customer rating | Revenue | SOP compliance %

**Charts**:
- Quality score trend line (mine vs. location avg vs. network avg)
- Service breakdown doughnut (by category)
- SOULSKIN impact: bar showing avg rating of sessions with vs. without SOULSKIN

**Skill Level Card**:
Visual L1 → L2 → L3 progress bar. Current level gold-highlighted.
Gap items: "To reach L2: Complete Advanced Color Training + 50 more color services"
"View Training Plan" button.

**Recent Quality Assessments**: Table of last 10 with drill-down.

---
#### MY TRAINING  |  `/stylist/training`
**My Learning Path**: Visual roadmap from current level to L3.
SOULSKIN Certification module shown as a special purple milestone.

**Completed**: table with certificate download.
**Available**: course cards with "Enroll" button.
**SOULSKIN Training Module**: if not certified — prominent card: "Unlock SOULSKIN — Certified Emotional Intelligence for Beauty"

---

### 5.4 SALON MANAGER PORTAL  |  `/manager/*`
Desktop-primary. Real-time operations control.

**Sidebar Nav**:
🏠 Dashboard | 📅 Today | 👥 Team | 📋 Bookings | 🚶 Queue | ⭐ Quality | 🪄 SOPs | 🔮 Trends | 📊 Reports | 💬 Feedback | 🔔 Alerts | ⚙️ Settings

---
#### MANAGER DASHBOARD  |  `/manager/dashboard`

**Live Banner** (auto-refresh 30s):
Chairs in use / capacity | Stylists on duty | Queue: X waiting | Est. wait: X min | Revenue today: ₹XX,XXX

**KPI Row**: Revenue today vs target | Services | Avg quality | No-shows | New customers | SOULSKIN sessions today

**Live Floor Map**: Visual grid of chairs
- Each chair: stylist name, customer, service, step progress bar, time remaining
- Color: Available (dim) | In Progress (teal) | SOULSKIN Active (violet) | Needs Attention (red)

**Smart Queue Panel** (right column):
- Live queue list: name, service, wait time
- "Assign" button for each waiting customer
- AI estimated wait: "Based on current load: ~22 minutes for next available chair"

**Quality Alerts**: Red flagged sessions below threshold.
**SOULSKIN Today**: Number of soul readings done. Archetype distribution pie chart.
**Climate Advisory**: Today's weather alert for beauty recommendations.
**Trend Alert**: New trend card if detected.
**Attrition Alerts**: Staff at HIGH risk highlighted.

---
#### SMART QUEUE  |  `/manager/queue`
Real-time queue management for the location.

**Live Queue Board**: Kanban-style
Columns: 🚶 Waiting | 💇 In Service | ✅ Done

Each card: customer name, service, wait time, assigned stylist.
Drag-and-drop between columns.
"Notify Customer" button on each waiting card → sends WhatsApp "Your stylist is ready"

**Add Walk-in** button → modal: name, phone, service, preferred stylist → adds to queue.

**Wait Time Display**: Large current wait estimate. Color: green (<15 min) | amber (15-30) | red (>30)

**Stylist Availability**: Row of all staff with status chips.

---
#### SOULSKIN ANALYTICS  |  `/manager/soulskin`
How SOULSKIN is affecting the salon.

**KPI Cards**: Sessions done this month | Avg rating with SOULSKIN vs without | Most common archetype | SOULSKIN-certified staff count

**Archetype Distribution**: Donut chart of archetypes this month.

**Rating Impact Chart**: Side-by-side bar — bookings with SOULSKIN vs without. Clear proof of impact.

**Stylist SOULSKIN Adoption**: Table — each stylist, how many SOULSKIN sessions, their avg rating when using it.

**Sample Soul Journals** (anonymized): last 5 soul journal entries for inspiration/quality check.

---
#### QUALITY SCORES, SOPs, TEAM, BOOKINGS, REPORTS, FEEDBACK, ALERTS — same as V1 design but with SOULSKIN-specific columns added. Each quality assessment now also shows soulskin_alignment_score. Reports include SOULSKIN impact analysis.

---

### 5.5 FRANCHISE OWNER, REGIONAL MANAGER, SUPER ADMIN PORTALS

Same structure as V1 but all dashboards now include:
- SOULSKIN session volume by location
- Archetype distribution across region/network
- Climate recommendation impact on service mix
- AR Smart Mirror adoption rate
- Digital Beauty Twin adoption rate
- Journey Plan generation rate

**Super Admin — AI Engine Dashboard** `/admin/ai`:
New sections added:
- SOULSKIN Engine: prompts fired today, avg LLM response time, quality flag count
- AR Mirror: sessions today, most tried styles, conversion to booking rate
- Mood Detection: detections today, archetype alignment rate with mood suggestion
- Digital Twin: twins active, simulations run, consent rate
- Climate Engine: cities tracked, last refresh time, alerts triggered
- Journey Planner: plans generated, on-track rate, milestone completion rate

---

## PART 6: SHARED COMPONENTS
(Same as V1, with these additions)

### 6.1 SOULSKIN Archetype Badge
Reusable pill component. Shows archetype icon + name in archetype color.
Used in: session page, customer passport, team list, booking cards.

### 6.2 Climate Alert Banner
Dismissible banner component. Shown site-wide when UV > 8 or AQI > 200.
"⚠️ High UV in Chennai today (9.2) — recommend UV-protective services to all customers"
Gold background. Teal CTA.

### 6.3 Beauty Score Ring
SVG ring visualization. 0-100. Color gradient: red (0-40) → amber (41-60) → teal (61-80) → gold (81-100).
Used in customer passport, customer list rows, customer cards.

### 6.4 Digital Twin Viewer
Three.js canvas component, embedded in any page.
Props: customer_id, view_mode (current | simulation | side-by-side).
Controls: rotate, zoom. Renders lightweight .glb model from S3.

### 6.5 AR Try-On Component
Full-screen or embedded mode. MediaPipe WebGL canvas.
Props: mode (hairstyle | hair_color | makeup), on_save callback.

---

## PART 7: KEY WORKFLOWS

### 7.1 Booking Workflow (ACID Transaction) — same as V1

### 7.2 SOULSKIN Session Workflow
```
1. Stylist opens SOULSKIN for a booked customer
2. POST /soulskin/sessions → creates session record linked to booking
3. 3 questions shown to customer (on stylist tablet or customer's phone)
4. Customer answers submitted → PATCH /soulskin/sessions/{id}
5. POST /soulskin/sessions/{id}/generate → Celery task:
   a. LLM (GPT-4o) receives: song + colour + word + customer beauty passport summary
   b. LLM generates: soul_reading (3 lines) + archetype assignment + archetype_reason
   c. LLM generates: service_protocol + colour_direction + sensory_environment +
                      touch_protocol + custom_formula + stylist_script + mirror_monologue
   d. LLM generates: private journal entry (written as customer's voice)
   e. All fields saved to soulskin_sessions table
6. Archetype pushed to customer profile → archetype_history updated
7. Service session SOPs loaded with soulskin_overlays for this archetype
8. Stylist sees: archetype banner + stylist script on their session page
9. On session complete: journal entry finalized + sent to customer via WhatsApp
10. Customer sees soul journal entry in their app
```

### 7.3 Mood Detection Workflow
```
1. Optional: at check-in, tablet camera faces customer briefly
2. Consent prompt: "May we take a quick mood reading? (improves your experience)"
3. If consent given: POST /mood/detect with image
4. Server-side: FER model analyzes facial expression
5. Returns: detected_emotion + energy_level + recommended_archetype + service_adjustment
6. If no SOULSKIN session done: suggest archetype from mood
7. Mood data used to adjust:
   - Service recommendations
   - Music/ambiance settings (if smart speaker integrated)
   - Stylist alert: "Customer appears stressed — gentle approach recommended"
8. Image NOT stored (privacy rule). Only emotion scores stored.
```

### 7.4 AI Scan + Digital Beauty Twin Workflow
```
1. Customer opens camera in app (Beauty Passport → "Rescan" or Mirror page)
2. MediaPipe runs in-browser: face detection, position guidance, capture
3. Image uploaded to S3 via POST /customers/{id}/scan
4. Celery task triggered:
   a. MediaPipe server-side: face mesh landmarks extracted
   b. Hair region segmented: color, texture, damage assessed
   c. Skin analysis: tone, type, concerns scored (custom PyTorch model)
   d. Emotion detection run (FER model) if mood_detection feature enabled
   e. All fields updated in customer_profiles
   f. beauty_score recalculated
   g. Digital Twin: 3D model rebuilt from new facial landmarks
   h. Future simulation: new projection generated based on updated diagnostics
   i. Recommendations regenerated by LLM
5. Customer notified: "Your Beauty Passport has been updated"
6. Digital twin viewer refreshed in app
```

### 7.5 Climate Recommendation Workflow (Daily Cron)
```
Runs at 5:30am every day for all active location cities.
1. Fetch all unique cities from locations table
2. For each city: call OpenWeatherMap API
   - temperature, humidity, UV index, AQI (from AirVisual API or similar), weather condition
3. Update climate_recommendations table (upsert for today's date)
4. Check thresholds:
   - UV > 8 → trigger is_alert = TRUE
   - AQI > 200 → trigger is_alert = TRUE
5. If alert triggered: push notification to all managers in that city
6. All customer portals in that city show climate card updated
7. AR Mirror climate suggestions refreshed
8. Trend engine reads climate data as a signal for seasonal service demand
```

### 7.6 Smart Queue AI Estimation
```
Wait time estimation algorithm runs every 2 minutes per active location.

Inputs:
  - current_sessions: list of active service_sessions with steps remaining + benchmark per step
  - staff_availability: stylists on duty, break schedules
  - queue_entries: current waiters with service_id
  - historical_service_duration: p90 actual duration per service per stylist

Algorithm:
  For each available/soon-available stylist:
    - Calculate: time remaining on current session (steps left × avg step duration)
    - Calculate: their queue position for next customer
  
  For each queue entry:
    - Match to earliest available qualified stylist
    - Estimated wait = time that stylist becomes available + buffer 5 min
  
Output:
  - estimated_wait_mins for each queue entry
  - Update smart_queue_entries.estimated_wait_mins
  - If wait increased by > 10 min: send WhatsApp update to customer
```

### 7.7 Quality Scoring
```
After every completed session:

sop_compliance_score = (steps_completed without deviation / total_steps) × 100

timing_score = 100 − clamp(|actual_duration − benchmark| / benchmark × 100, 0, 50)

customer_rating_score = customer_rating × 20  (1-5 → 20-100)

soulskin_alignment_score (if SOULSKIN active):
  - Did service_protocol match what was actually done?
  - Did session_duration match SOULSKIN recommendation?
  - Score: 0-100 based on alignment
  - If SOULSKIN not active: this field is null

overall_score = (sop_compliance × 0.25) + (timing × 0.15) + (customer_rating × 0.50) + (soulskin_alignment × 0.10 if applicable, else redistribute)

Thresholds:
  ≥ 85: Excellent → green
  70-84: Good → teal  
  55-69: Needs Improvement → amber
  < 55: Poor → red flag → manager alert
```

---

## PART 8: PWA — FULL SPECIFICATION

### 8.1 What is Installed as a PWA
AURA ships as a full Progressive Web App. Every portal is installable.

**Installable Portals**:
- Customer App (/app/*): installable, offline beauty passport view
- Stylist App (/stylist/*): installable, fully offline-capable session page

**Supported Platforms**:
- Android: Chrome 67+ (full PWA — install, push, offline)
- iOS: Safari 16.4+ (install to home screen, partial push)
- Desktop: Chrome/Edge (install as desktop app)

### 8.2 Web App Manifest
```json
{
  "name": "AURA — Beauty Intelligence",
  "short_name": "AURA",
  "description": "AI-powered salon intelligence by Naturals",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0A0F",
  "theme_color": "#C9A96E",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "screenshots": [
    { "src": "/screenshots/passport.png", "sizes": "390x844", "type": "image/png" },
    { "src": "/screenshots/session.png", "sizes": "390x844", "type": "image/png" }
  ],
  "categories": ["beauty", "health", "lifestyle"],
  "lang": "en",
  "orientation": "portrait"
}
```

### 8.3 Service Worker Caching Strategy (Workbox 7)

```
Cache Strategy per Resource Type:

Static Assets (JS, CSS, fonts, icons):
  Strategy: CacheFirst
  Max age: 30 days
  Serves cached version immediately, updates in background

API responses (GET requests):
  Strategy: NetworkFirst with offline fallback
  Max age: 5 minutes
  If network fails: serve cached version + show "offline" indicator

Critical Offline Data (pre-cached on login):
  - Today's bookings for this stylist
  - SOP data for today's services
  - Customer beauty passport for today's customers
  - AI coaching prompts for today's sessions (pre-generated)
  - Archetype descriptions
  Pre-cache triggered: on login + daily at 7am (background sync)

Images (S3 URLs):
  Strategy: CacheFirst
  Max age: 24 hours
  Stale-while-revalidate for profile images

Non-cacheable (never cache):
  - Auth endpoints
  - Payment endpoints
  - POST/PATCH/DELETE requests
```

### 8.4 Offline Actions (IndexedDB Queue)

When offline, the following actions are queued in IndexedDB and synced on reconnect:

```
Stylist Session:
  - step_completion: {session_id, step_number, completed_at, products_used}
  - deviation_log: {session_id, step, reason, logged_at}
  - session_complete: {session_id, final_notes, completed_at}
  - photo_upload: {session_id, type (before/after), image_blob}

Customer Passport:
  - lifestyle_update: {customer_id, field, value, updated_at}

All sync via POST /sessions/{id}/sync endpoint on reconnect.
Conflict resolution: server is authoritative. Offline actions applied as events with timestamps.
If conflict detected: manager notified.
```

### 8.5 Push Notifications

**Notification Types by Role**:

CUSTOMER:
- Booking reminder (24h before + 2h before)
- Queue update ("Your stylist is ready — X is waiting for you")
- Journey milestone reminder ("This week: recommended Vitamin C Facial")
- SOULSKIN soul journal shared (after visit)
- Home care weekly tip
- Climate alert ("High UV today in Chennai — protect your hair/skin")

STYLIST:
- New booking assigned
- Quality flag on completed session
- Training deadline reminder
- Attrition risk alert (own risk, shown gently as "career growth reminder")
- SOULSKIN session request

MANAGER:
- Quality flag (session below threshold)
- HIGH attrition risk staff alert
- New trend detected (relevant to location)
- Queue growing (wait > 30 min)
- Climate alert for their city

**Push implementation**:
- Token registered on login: POST /auth/me/push-token
- Token stored in users.push_token
- Celery sends via Web Push Protocol (for PWA) + WhatsApp as fallback

### 8.6 Install Prompt Strategy

**When to show install prompt**:
- Customer portal: after second visit to app (not on first load)
- Stylist portal: after first login
- Design: custom bottom sheet (not browser default)
  - AURA icon + "Add to Home Screen"
  - Benefit text: "Instant access to your Beauty Passport"
  - "Install" (primary) + "Not now" (secondary)
- On iOS: show manual instruction ("Tap Share → Add to Home Screen")

---

## PART 9: SECURITY & COMPLIANCE

### 9.1 DPDP Act 2023 Compliance
```
- Explicit consent on register for: data collection, AI analysis, mood detection (separate consent)
- Consent stored: user_id + consent_type + timestamp + consent_version + IP hash
- Right to access: GET /customers/{id}/export — full data export as JSON/PDF
- Right to erasure: DELETE /customers/{id} → soft delete + 30-day hard delete queue
- Mood detection: additional consent required. Face images never stored.
- Digital Twin: separate consent checkbox. Customer can delete twin anytime.
- SOULSKIN journal: customer owns their journal. Can export or delete.
- Data retention: booking data 7 years (GST). Beauty profiles until deletion request.
- Breach notification: < 72 hours to CERT-In
- Penalty awareness: up to ₹250 crore for significant violations
```

### 9.2 Authentication
```
- Password: bcrypt, cost factor 12
- JWT: RS256 asymmetric signing
- Refresh tokens: httpOnly Secure SameSite=Strict cookie
- Token rotation on every refresh
- 5 failed attempts → 30-minute lockout (tracked in Redis)
- Rate limit: 10 req/min on /auth/* per IP
- OTP: 6-digit, 10-minute expiry, SHA-256 hashed in DB
```

### 9.3 API Security
```
- All routes require JWT except register/login
- RBAC on every endpoint (FastAPI dependency)
- PostgreSQL RLS as second layer
- Input validation: Pydantic on all incoming data
- File uploads: MIME validation + 10MB limit + virus scan pipeline
- CORS: strict whitelist
- HTTPS only (HTTP → HTTPS at load balancer)
- S3 image URLs: pre-signed, expire 1 hour
- Rate limiting: 100 req/min authenticated, 10 req/min public
```

### 9.4 Sensitive Data Rules
```
- Customer scan images: encrypted at rest (S3 SSE-KMS), pre-signed URLs only
- Mood detection images: NEVER stored. Only processed and discarded.
- Allergy data: field-level encryption (AES-256)
- SOULSKIN journal entries: encrypted at rest, customer-owned
- Digital Twin models: encrypted, consent-gated access
- Payment data: never stored. Razorpay handles. Only transaction ID stored.
- Audit log: all data access + modifications logged (immutable, append-only)
```

---

## PART 10: SCALABILITY

### 10.1 Architecture for 1 → 1000+ Salons
```
Multi-tenancy: Shared schema + location_id filtering + PostgreSQL RLS
Connection pooling: PgBouncer (200 DB connections → 2000+ app users)
Read replicas: All analytics queries routed to RDS Read Replica
Caching: Redis for sessions, queues, API responses
CDN: CloudFront for all static + PWA assets
Background jobs: Celery auto-scales on SQS queue depth
  - Separate queues: ai_analysis | notifications | reports | sync | climate | trends

Critical DB indexes:
  - bookings: (location_id, scheduled_at, status)
  - service_sessions: (booking_id) UNIQUE, (stylist_id, status)
  - quality_assessments: (stylist_id, created_at)
  - soulskin_sessions: (customer_id, created_at)
  - smart_queue_entries: (location_id, status, joined_queue_at)
  - customer_profiles: GiST on profile_embedding (pgvector)
  - climate_recommendations: (city, date_for) UNIQUE
  - trend_signals: (is_active, applicable_regions)
```

### 10.2 PWA Offline Architecture
```
Service Worker (Workbox 7):
  - Caches React app shell
  - Pre-caches today's critical data (SOPs, bookings, passports) at 7am
  - Background sync for offline session actions
  
IndexedDB (offline queue):
  - step_completions_queue
  - deviation_logs_queue
  - photo_upload_queue (stores image blobs until sync)
  
Sync endpoint:
  - POST /sessions/{id}/sync
  - Accepts batch of offline actions with timestamps
  - Idempotent (safe to retry)
  - Conflict resolution: server timestamp wins
```

---

## PART 11: SEED DATA FOR DEMO

```
Locations (5): NAT-TN-001 Anna Nagar Chennai | NAT-TN-002 T.Nagar Chennai |
               NAT-KA-001 Koramangala Bangalore | NAT-MH-001 Bandra Mumbai | NAT-DL-001 CP Delhi

Users (1 per role + 3 extra customers for demo):
  super@aura.in         / SUPER_ADMIN
  regional@aura.in      / REGIONAL_MANAGER (South India region)
  owner@aura.in         / FRANCHISE_OWNER (Anna Nagar location)
  manager@aura.in       / SALON_MANAGER (Anna Nagar)
  stylist@aura.in       / STYLIST — Meena, L2, specialization: hair_color + bridal
  customer@aura.in      / CUSTOMER — Priya Sharma, Chennai, Beauty Score 78, Archetype: BLOOM

Demo SOULSKIN sessions (3 pre-generated):
  Customer 1: Song="Kesariya" | Colour="Gold" | Word="Free" → Archetype: BLOOM
  Customer 2: Song="Numb" | Colour="Grey" | Word="Peace" → Archetype: STORM
  Customer 3: Song="Phir Le Aya Dil" | Colour="Red" | Word="Bold" → Archetype: PHOENIX

Services (12): Hair Cut | Hair Color | Balayage | Keratin | Bridal Makeup |
               Deep Facial | Scalp Treatment | Manicure | Pedicure | Eyebrow Threading |
               Head Massage | Glass Skin Facial (TRENDING)

SOPs (4 fully detailed): Hair Color | Balayage | Bridal Makeup | Deep Facial
Each SOP: all 5 languages + SOULSKIN overlays for all 5 archetypes

Trend Signals (3 active): Cherry Mocha Hair | Glass Skin Facial | Curtain Bangs

Climate Data: Pre-seeded for Chennai, Bangalore, Mumbai, Delhi (today's simulated data)

Bookings (60): across all locations, past 90 days, mix of statuses
Quality Assessments: for all completed bookings
SOULSKIN Sessions: 15 (with full generated content for demo)
Feedback: 40 entries across locations
Training Records: 3 per stylist
Beauty Journey Plans: 2 (active for demo customers)
Digital Beauty Twins: created for demo customers
AR Try-on History: 5 sessions for demo customer
```

---

## PART 12: REACT ROUTE TREE (COMPLETE)

```
App
├── PublicLayout (no auth)
│   ├── /                         Landing Page (3D, SOULSKIN preview)
│   ├── /login                    Login
│   ├── /register                 Register (3-step)
│   ├── /forgot-password
│   └── /reset-password
│
├── CustomerLayout [role: customer] PWA, mobile-first
│   ├── /app/dashboard            Home (climate card, AI recs, SOULSKIN teaser)
│   ├── /app/passport             Beauty Passport (all tabs)
│   ├── /app/mirror               AR Smart Mirror (WebGL, full-screen)
│   ├── /app/soulskin             SOULSKIN Entry Flow (3 questions → soul reveal)
│   ├── /app/book                 Book Appointment (4-step)
│   ├── /app/bookings             My Bookings
│   │   └── /app/bookings/:id     Booking Detail
│   ├── /app/journey              Beauty Journey Plan
│   ├── /app/homecare             Home Care Plan
│   └── /app/profile              Customer Profile + settings
│
├── StylistLayout [role: stylist] PWA, fully offline-capable
│   ├── /stylist/dashboard        Today's Schedule
│   ├── /stylist/session/:id      LIVE SESSION (offline-capable, SOULSKIN overlay)
│   ├── /stylist/soulskin/:id     SOULSKIN Flow for a customer
│   ├── /stylist/customers        My Customers
│   │   └── /stylist/customers/:id  Customer View (passport + soul history)
│   ├── /stylist/performance      My Performance (with SOULSKIN impact chart)
│   └── /stylist/training         My Training (SOULSKIN certification module)
│
├── ManagerLayout [role: salon_manager]
│   ├── /manager/dashboard        Manager Dashboard (live floor + queue + SOULSKIN stats)
│   ├── /manager/today            Today's Operations (Gantt)
│   ├── /manager/queue            Smart Queue Board (kanban)
│   ├── /manager/team             My Team
│   │   └── /manager/team/:id     Staff Detail
│   ├── /manager/bookings         All Bookings
│   │   └── /manager/bookings/:id Booking Detail
│   ├── /manager/quality          Quality Scores
│   │   └── /manager/quality/sessions/:id  Session Review
│   ├── /manager/soulskin         SOULSKIN Analytics
│   ├── /manager/sops             SOP Management
│   │   ├── /manager/sops/:id     SOP Detail (with archetype overlays)
│   │   └── /manager/sops/:id/edit SOP Editor (with SOULSKIN overlay editor)
│   ├── /manager/trends           Trend Intelligence + Climate
│   ├── /manager/reports          Reports (all types)
│   ├── /manager/feedback         Customer Feedback
│   ├── /manager/alerts           Alerts Hub
│   └── /manager/settings         Location Settings
│
├── FranchiseLayout [role: franchise_owner]
│   ├── /franchise/dashboard      Franchise Overview
│   ├── /franchise/locations      My Locations (with SOULSKIN + AR adoption rates)
│   │   └── /franchise/locations/:id  Location Detail
│   ├── /franchise/revenue        Revenue
│   ├── /franchise/quality        Quality Overview
│   ├── /franchise/staff          All Staff + Attrition Risk
│   ├── /franchise/compare        Location Comparison
│   └── /franchise/reports        Reports
│
├── RegionalLayout [role: regional_manager]
│   ├── /regional/dashboard       Regional Dashboard
│   ├── /regional/map             Region Map (with SOULSKIN + quality overlay)
│   ├── /regional/locations       All Locations
│   │   └── /regional/locations/:id  Location Detail
│   ├── /regional/revenue         Revenue
│   ├── /regional/quality         Quality Network
│   ├── /regional/staff           Staff Intelligence
│   ├── /regional/trends          Trend Alerts
│   ├── /regional/compare         Location Comparison
│   └── /regional/reports         Reports
│
└── AdminLayout [role: super_admin]
    ├── /admin/dashboard          Command Center (network-wide live view)
    ├── /admin/map                Network Map (India, all locations)
    ├── /admin/locations          All Locations
    │   └── /admin/locations/:id  Location Detail
    ├── /admin/users              All Users
    │   └── /admin/users/:id      User Detail + Role Management
    ├── /admin/revenue            Network Revenue
    ├── /admin/quality            Quality Network
    ├── /admin/trends             Trend Intelligence Engine
    ├── /admin/ai                 AI Engine Dashboard (all models, queues, costs)
    ├── /admin/soulskin           SOULSKIN Network Analytics
    ├── /admin/bi                 Business Intelligence (full BI suite)
    ├── /admin/training           Training Network + ROI
    ├── /admin/config             System Configuration
    └── /admin/rbac               Roles & Permissions + Audit Log
```

---

## PART 13: UNIQUE DIFFERENTIATORS — COMPETITION SUMMARY

What no other salon platform in the world has built:

```
1. SOULSKIN — World's first Emotion-to-Beauty Intelligence System
   No competitor does soul reading → archetype → full sensory experience design.
   This alone makes AURA unforgettable.

2. Offline-first stylist session with AI coaching
   Works in Tier-2/3 with zero connectivity. Pre-cached SOPs + AI prompts.
   No salon software is offline-capable during live service delivery.

3. Digital Beauty Twin with future simulation
   Longitudinal 3D face model updated per visit. Shows predicted skin in 3/6 months.
   Unique to beauty industry — not deployed in any salon chain today.

4. Climate-aware recommendations — real-time, per-city
   UV + humidity + AQI feeding service recommendations and AR Mirror suggestions.
   India-specific and genuinely useful for a country spanning 5 climate zones.

5. Training investment → revenue outcome pipeline
   First system to close the loop: training → skill score → quality score → revenue.
   No competitor measures training ROI in the salon industry.

6. Multilingual SOULSKIN (5 Indian languages)
   Soul readings, SOP guidance, WhatsApp messages — all in Tamil, Hindi, Telugu, Kannada, English.
   Built for India's linguistic reality, not adapted from a Western product.
```

---

*AURA — Unified Salon Intelligence Platform*
*Master System Design Document — Version 2.0*
*Naturals BeautyTech Hackathon 2026 | Challenge 5: Open Innovation*
*Stack: FastAPI + React + SQLAlchemy + PostgreSQL | Full PWA*
