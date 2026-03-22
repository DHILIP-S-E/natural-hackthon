"""AURA — FastAPI Application Entry Point."""
from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json


class DecimalSafeEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal (from SQLite Numeric columns)."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class DecimalSafeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, cls=DecimalSafeEncoder, ensure_ascii=False).encode("utf-8")

from app.config import settings
from app.routers import (
    auth, locations, staff, customers, bookings, soulskin, services, analytics,
    sessions, queue, trends, climate, feedback, notifications, homecare,
    mood, twin, mirror, journey, sops, quality, training, roles,
)

# ── Import all agent modules to trigger registration ──
from app.agents import get_all_agents, get_agents_by_track, get_agents_by_ps
import app.agents.track1_standardization  # noqa: F401 — 12 agents
import app.agents.track2_staff            # noqa: F401 — 11 agents
import app.agents.track3_personalization  # noqa: F401 — 10 agents
import app.agents.track4_trends           # noqa: F401 — 10 agents
import app.agents.track5_experience       # noqa: F401 — 10 agents
import app.agents.track6_intelligence     # noqa: F401 — 10 agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    agents = get_all_agents()
    print(f"[AURA] v2.0 starting up -- {settings.APP_ENV} mode")
    print(f"[DB] {settings.DATABASE_URL[:40]}...")
    print(f"[AGENTS] {len(agents)} business logic agents registered across 6 tracks")
    for track in ["standardization", "staff", "personalization", "trends", "experience", "intelligence"]:
        track_agents = get_agents_by_track(track)
        print(f"   Track [{track}]: {len(track_agents)} agents")
    yield
    print("[AURA] shutting down")


app = FastAPI(
    default_response_class=DecimalSafeJSONResponse,
    title="AURA — Unified Salon Intelligence Platform",
    description="AI-powered salon intelligence system for Naturals BeautyTech. "
                "Covers Beauty Passport, SOULSKIN Engine, AR Smart Mirror, "
                "Digital Beauty Twin, AI Stylist Assistant, Trend Intelligence, "
                "Staff Intelligence, and Salon BI Dashboard. "
                "63+ business logic agents across 6 challenge tracks.",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API prefix
API = settings.API_V1_PREFIX

# ── Register all CRUD routers ──
app.include_router(auth.router, prefix=API)
app.include_router(locations.router, prefix=API)
app.include_router(staff.router, prefix=API)
app.include_router(customers.router, prefix=API)
app.include_router(bookings.router, prefix=API)
app.include_router(soulskin.router, prefix=API)
app.include_router(services.router, prefix=API)
app.include_router(analytics.router, prefix=API)
app.include_router(sessions.router, prefix=API)
app.include_router(queue.router, prefix=API)
app.include_router(trends.router, prefix=API)
app.include_router(climate.router, prefix=API)
app.include_router(feedback.router, prefix=API)
app.include_router(notifications.router, prefix=API)
app.include_router(homecare.router, prefix=API)
app.include_router(mood.router, prefix=API)
app.include_router(twin.router, prefix=API)
app.include_router(mirror.router, prefix=API)
app.include_router(journey.router, prefix=API)
app.include_router(sops.router, prefix=API)
app.include_router(quality.router, prefix=API)
app.include_router(training.router, prefix=API)
app.include_router(roles.router, prefix=API)

# ── Register all 63 agent endpoints ──
agent_router = APIRouter(prefix="/agents", tags=["AI Agents"])

for agent_action in get_all_agents():
    method = agent_action.method.lower()
    route_fn = getattr(agent_router, method, agent_router.get)
    route_fn(
        agent_action.path.replace("/agents", ""),
        response_model=None,
        summary=agent_action.description,
        tags=[f"Track: {agent_action.track.title()}", agent_action.feature.title()],
    )(agent_action.handler)

app.include_router(agent_router, prefix=API)


# ── Agent Discovery Endpoints ──

@app.get("/api/v1/agents/registry", tags=["Agent Discovery"])
async def agent_registry():
    """List all registered business logic agents with metadata."""
    agents = get_all_agents()
    return {
        "total_agents": len(agents),
        "tracks": {
            "standardization": {"count": len(get_agents_by_track("standardization")), "ps_range": "PS-01.01 — PS-01.10"},
            "staff": {"count": len(get_agents_by_track("staff")), "ps_range": "PS-02.01 — PS-02.10"},
            "personalization": {"count": len(get_agents_by_track("personalization")), "ps_range": "PS-03.01 — PS-03.10"},
            "trends": {"count": len(get_agents_by_track("trends")), "ps_range": "PS-04.01 — PS-04.10"},
            "experience": {"count": len(get_agents_by_track("experience")), "ps_range": "PS-05.01 — PS-05.10"},
            "intelligence": {"count": len(get_agents_by_track("intelligence")), "ps_range": "PS-06.01 — PS-06.10"},
        },
        "agents": [{
            "name": a.name,
            "description": a.description,
            "track": a.track,
            "feature": a.feature,
            "method": a.method.upper(),
            "path": f"/api/v1{a.path}",
            "roles": a.roles,
            "ps_codes": a.ps_codes,
            "requires_ai": a.requires_ai,
            "offline_capable": a.offline_capable,
        } for a in agents],
    }


@app.get("/api/v1/agents/registry/{track}", tags=["Agent Discovery"])
async def agents_by_track(track: str):
    """List agents for a specific track."""
    agents = get_agents_by_track(track)
    if not agents:
        return {"error": f"Track '{track}' not found", "available_tracks": [
            "standardization", "staff", "personalization", "trends", "experience", "intelligence"
        ]}
    return {
        "track": track,
        "count": len(agents),
        "agents": [{
            "name": a.name,
            "description": a.description,
            "feature": a.feature,
            "method": a.method.upper(),
            "path": f"/api/v1{a.path}",
            "ps_codes": a.ps_codes,
        } for a in agents],
    }


@app.get("/api/v1/agents/ps/{ps_code}", tags=["Agent Discovery"])
async def agents_by_problem_statement(ps_code: str):
    """Find agents that address a specific problem statement (e.g. PS-01.01)."""
    agents = get_agents_by_ps(ps_code)
    return {
        "ps_code": ps_code,
        "agents_found": len(agents),
        "agents": [{
            "name": a.name,
            "description": a.description,
            "track": a.track,
            "method": a.method.upper(),
            "path": f"/api/v1{a.path}",
        } for a in agents],
    }


@app.get("/")
async def root():
    agents = get_all_agents()
    return {
        "name": "AURA — Unified Salon Intelligence Platform",
        "version": "2.0.0",
        "status": "operational",
        "agents_registered": len(agents),
        "modules": [
            "Beauty Passport", "SOULSKIN Engine", "AI Smart Mirror",
            "Digital Beauty Twin", "AI Stylist Assistant",
            "Trend Intelligence", "Staff Intelligence", "Salon BI Dashboard",
        ],
        "challenge_tracks": [
            "Track 1: Standardising Salon Experience (12 agents)",
            "Track 2: Reducing Staff Dependency (11 agents)",
            "Track 3: Hyper-Personalised Beauty (10 agents)",
            "Track 4: AI-Based Trend Prediction (10 agents)",
            "Track 5: AI Customer Experience (10 agents)",
            "Track 6: Salon Business Intelligence (10 agents)",
        ],
        "docs": "/api/docs",
        "agent_registry": "/api/v1/agents/registry",
    }


@app.get("/health")
async def health_check():
    agents = get_all_agents()
    return {
        "status": "healthy",
        "app": "AURA",
        "version": "2.0.0",
        "agents_loaded": len(agents),
    }
