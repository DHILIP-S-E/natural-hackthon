"""Customer profile router — face scan (Gemini) + profile save/retrieve.

Flow:
  POST /profile/scan-face  → photo base64 + Firebase URL → Gemini analysis → stored
  POST /profile/save-edits → user-edited fields → stored in CustomerProfile
  GET  /profile/{customer_id} → fetch current profile
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from models.user import User
from models.customer import CustomerProfile
from utils.secrets import settings

router = APIRouter(prefix="/profile", tags=["Customer Profile"])

GEMINI_FACE_PROMPT = """Analyze this customer's hair and skin from the photo.

Return ONLY a JSON object with these exact keys (no markdown, no explanation):
{
  "hair": {
    "type": "<one of: 1A/1B/1C/2A/2B/2C/3A/3B/3C/4A/4B/4C>",
    "color": "<natural color description>",
    "condition": "<one of: Healthy/Slightly damaged/Moderate damage/Severely damaged>",
    "concerns": ["<items from: Frizz/Breakage/Dryness/Oiliness/Color-fade/Scalp irritation/Hair fall/Dandruff>"],
    "scalp": "<Healthy/Dry/Oily/Flaky>"
  },
  "skin": {
    "tone": "<one of: Fair/Light/Medium/Olive/Dark/Deep>",
    "condition": "<one of: Dry/Oily/Combination/Normal/Sensitive>",
    "issues": ["<visible issues if any, e.g. Acne/Pigmentation/Dullness>"]
  },
  "overall_confidence": <0.0 to 1.0>
}"""

_CONDITION_TO_DAMAGE: Dict[str, int] = {
    "Healthy": 1,
    "Slightly damaged": 2,
    "Moderate damage": 3,
    "Severely damaged": 4,
}


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ScanFaceRequest(BaseModel):
    customer_id: str
    photo_base64: str
    photo_url: str


class EditedProfileData(BaseModel):
    hair_type: str = ""
    hair_condition: str = ""
    hair_concerns: List[str] = []
    skin_tone: str = ""
    skin_condition: str = ""
    allergies: List[str] = []


class SaveProfileRequest(BaseModel):
    customer_id: str
    analysis_id: str
    edited_profile: EditedProfileData


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _call_gemini_vision(photo_base64: str) -> Dict[str, Any]:
    """Call Gemini vision API. Falls back to mock data if key not configured."""
    if not settings.GEMINI_API_KEY:
        return {
            "hair": {
                "type": "3B",
                "color": "Dark brown",
                "condition": "Moderate damage",
                "concerns": ["Frizz", "Breakage"],
                "scalp": "Healthy",
            },
            "skin": {
                "tone": "Medium",
                "condition": "Combination",
                "issues": [],
            },
            "overall_confidence": 0.85,
        }

    import httpx

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": GEMINI_FACE_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": photo_base64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {"temperature": 0.1},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error {resp.status_code}: {resp.text[:300]}",
        )

    result = resp.json()
    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        # Strip markdown code fences if present
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    except (KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=502, detail=f"Could not parse Gemini response: {exc}"
        ) from exc


def _build_profile_response(profile: CustomerProfile, analysis_id: str = "") -> dict:
    meta = profile.chemical_history or {}
    hair_concerns = meta.get("hair_concerns", [])
    return {
        "profile_id": str(profile.id),
        "customer_id": str(profile.user_id),
        "face_analysis_id": meta.get("analysis_id", analysis_id),
        "hair_type": profile.hair_type or "",
        "hair_condition": meta.get("hair_condition", ""),
        "hair_concerns": hair_concerns,
        "skin_tone": profile.skin_tone or "",
        "skin_condition": profile.skin_type or "",
        "allergies": profile.known_allergies or [],
        "profile_complete": bool(profile.scan_image_url),
        "user_edited": meta.get("user_edited", False),
        "confidence": meta.get("confidence", 0.0),
        "scan_image_url": profile.scan_image_url or "",
        "last_scan_at": profile.last_scan_at.isoformat() if profile.last_scan_at else None,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/scan-face")
async def scan_face(
    req: ScanFaceRequest,
    db: AsyncSession = Depends(get_db),
):
    """Upload photo → Gemini analysis → store in CustomerProfile."""
    analysis = await _call_gemini_vision(req.photo_base64)

    hair = analysis.get("hair", {})
    skin = analysis.get("skin", {})
    analysis_id = str(uuid.uuid4())

    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == req.customer_id)
    )
    profile = result.scalar_one_or_none()

    # Store analysis details that don't have dedicated columns in chemical_history JSON
    analysis_meta = {
        "analysis_id": analysis_id,
        "photo_url": req.photo_url,
        "hair_condition": hair.get("condition", ""),
        "hair_concerns": hair.get("concerns", []),
        "hair_scalp": hair.get("scalp", ""),
        "confidence": analysis.get("overall_confidence", 0.0),
        "skin_issues": skin.get("issues", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_edited": False,
    }

    now = datetime.now(timezone.utc)

    if profile is None:
        profile = CustomerProfile(
            user_id=req.customer_id,
            hair_type=hair.get("type"),
            natural_hair_color=hair.get("color"),
            hair_damage_level=_CONDITION_TO_DAMAGE.get(hair.get("condition", ""), None),
            skin_tone=skin.get("tone"),
            skin_type=skin.get("condition"),
            primary_skin_concerns=skin.get("issues", []),
            scan_image_url=req.photo_url,
            last_scan_at=now,
            chemical_history=analysis_meta,
        )
        db.add(profile)
    else:
        profile.hair_type = hair.get("type")
        profile.natural_hair_color = hair.get("color")
        profile.hair_damage_level = _CONDITION_TO_DAMAGE.get(hair.get("condition", ""), None)
        profile.skin_tone = skin.get("tone")
        profile.skin_type = skin.get("condition")
        profile.primary_skin_concerns = skin.get("issues", [])
        profile.scan_image_url = req.photo_url
        profile.last_scan_at = now
        profile.chemical_history = analysis_meta
        profile.updated_at = now

    await db.commit()
    await db.refresh(profile)

    return {
        "analysis_id": analysis_id,
        "customer_id": req.customer_id,
        "photo_url": req.photo_url,
        "analysis": analysis,
    }


@router.post("/save-edits")
async def save_profile_edits(
    req: SaveProfileRequest,
    db: AsyncSession = Depends(get_db),
):
    """Save user-edited profile fields back to CustomerProfile."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == req.customer_id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    edited = req.edited_profile
    now = datetime.now(timezone.utc)

    # Update dedicated columns
    profile.hair_type = edited.hair_type or profile.hair_type
    profile.hair_damage_level = _CONDITION_TO_DAMAGE.get(
        edited.hair_condition, profile.hair_damage_level
    )
    profile.skin_tone = edited.skin_tone or profile.skin_tone
    profile.skin_type = edited.skin_condition or profile.skin_type
    profile.known_allergies = edited.allergies
    profile.updated_at = now

    # Keep extra fields in chemical_history
    existing_meta = profile.chemical_history or {}
    profile.chemical_history = {
        **existing_meta,
        "analysis_id": req.analysis_id,
        "hair_condition": edited.hair_condition,
        "hair_concerns": edited.hair_concerns,
        "user_edited": True,
        "edited_at": now.isoformat(),
    }

    await db.commit()
    await db.refresh(profile)

    return {
        "profile_id": str(profile.id),
        "customer_id": req.customer_id,
        "hair_type": edited.hair_type,
        "hair_condition": edited.hair_condition,
        "hair_concerns": edited.hair_concerns,
        "skin_tone": edited.skin_tone,
        "skin_condition": edited.skin_condition,
        "allergies": edited.allergies,
        "profile_complete": True,
        "user_edited": True,
    }


@router.get("/{customer_id}")
async def get_profile(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch customer profile — returns empty strings if no face scan done yet."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _build_profile_response(profile)
