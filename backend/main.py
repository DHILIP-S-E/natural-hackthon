"""AURA — FastAPI Application Entry Point (flat structure).

Run with:
    uvicorn main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

from utils.secrets import settings
from routers import (
    auth, locations, staff, customers, bookings, soulskin, services, analytics,
    sessions, queue, trends, climate, feedback, notifications, homecare,
    mood, twin, mirror, journey, sops, quality, training, roles,
    skintone, eco, voice, aurascore, upsell, consultation, chatbot, waittime,
    allergy, twin_timeline, franchise_dashboard, loyalty, config,
    customer_auth, customer_profile,
)

from agents import get_all_agents, get_agents_by_track, get_agents_by_ps
import agents.track1_standardization  # noqa: F401
import agents.track2_staff            # noqa: F401
import agents.track3_personalization  # noqa: F401
import agents.track4_trends           # noqa: F401
import agents.track5_experience       # noqa: F401
import agents.track6_intelligence     # noqa: F401

from middleware.logging_middleware import logging_middleware


class DecimalSafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class DecimalSafeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, cls=DecimalSafeEncoder, ensure_ascii=False).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    agents = get_all_agents()
    print(f"[AURA] v2.0 starting up — {settings.APP_ENV} mode")
    print(f"[DB] {settings.DATABASE_URL[:40]}...")
    print(f"[AGENTS] {len(agents)} agents registered across 6 tracks")
    for track in ["standardization", "staff", "personalization", "trends", "experience", "intelligence"]:
        track_agents = get_agents_by_track(track)
        print(f"   Track [{track}]: {len(track_agents)} agents")
    yield
    print("[AURA] shutting down")


app = FastAPI(
    default_response_class=DecimalSafeJSONResponse,
    title="AURA — Unified Salon Intelligence Platform",
    description="AI-powered salon intelligence for Naturals BeautyTech. 63+ agents across 6 tracks.",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

app.middleware("http")(logging_middleware)

API = settings.API_V1_PREFIX

# ── CRUD routers ──────────────────────────────────────────────────────────────
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
app.include_router(skintone.router, prefix=API)
app.include_router(eco.router, prefix=API)
app.include_router(voice.router, prefix=API)
app.include_router(aurascore.router, prefix=API)
app.include_router(upsell.router, prefix=API)
app.include_router(consultation.router, prefix=API)
app.include_router(chatbot.router, prefix=API)
app.include_router(waittime.router, prefix=API)
app.include_router(allergy.router, prefix=API)
app.include_router(twin_timeline.router, prefix=API)
app.include_router(franchise_dashboard.router, prefix=API)
app.include_router(loyalty.router, prefix=API)
app.include_router(config.router, prefix=API)

# ── Mobile app routers ────────────────────────────────────────────────────────
app.include_router(customer_auth.router, prefix=API)
app.include_router(customer_profile.router, prefix=API)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "version": "2.0.0"}
