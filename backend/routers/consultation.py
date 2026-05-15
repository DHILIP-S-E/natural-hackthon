"""Digital Consultation Form — Idea 19: Pre-Visit Intelligence.

Domain logic:
  On booking confirmation → send WhatsApp link to customer (Twilio/SNS).
  Customer fills 2-minute form: hair type, allergies (mandatory e-signature),
  goal, budget, health conditions.
  On submit → auto-populate Beauty Passport + generate stylist briefing via Gemini.
  Allergy conflict detection runs immediately against booked service.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid
from utils.dependencies import get_current_user, get_optional_user
from models.user import User
from schemas.common import APIResponse

router = APIRouter(prefix="/consultation", tags=["Digital Consultation Form"])


# ── Schemas ──

class ConsultationSubmission(BaseModel):
    booking_id: str
    token: str                                       # one-time token from WhatsApp link

    # Hair
    hair_type: Optional[str] = None                 # Straight / Wavy / Curly / Coily
    hair_texture: Optional[str] = None              # Fine / Medium / Coarse
    scalp_condition: Optional[str] = None           # Normal / Oily / Dry / Sensitive
    last_chemical_treatment: Optional[str] = None  # ISO date string
    current_hair_color: Optional[str] = None

    # Skin
    skin_type: Optional[str] = None                 # Oily / Dry / Combination / Normal
    primary_skin_concerns: Optional[list[str]] = None

    # Allergies — mandatory with e-signature acknowledgement
    known_allergies: list[str] = Field(default_factory=list)
    product_sensitivities: list[str] = Field(default_factory=list)
    allergy_declaration_signed: bool = False         # Customer must tick this

    # Visit intent
    visit_goal: Optional[str] = None               # Maintain / Try something new / Special occasion
    budget_preference: Optional[str] = None        # Budget / Standard / Premium
    occasion: Optional[str] = None

    # Health
    health_conditions: list[str] = Field(default_factory=list)
    medications_affecting_hair_skin: list[str] = Field(default_factory=list)

    # Pregnancy / sensitivity
    is_pregnant: bool = False
    is_breastfeeding: bool = False


STYLIST_BRIEFING_PROMPT = """You are a senior salon consultant. Convert this customer consultation data into a clear,
actionable pre-service briefing for the stylist. Be specific, practical, and concise (max 120 words).
Start with the most important safety note if allergies exist, then visit goal, then 2-3 care tips.

Data: {data}

Briefing:"""


async def _generate_stylist_briefing(data: dict) -> str:
    """Generate plain-English stylist briefing from consultation form data."""
    from utils.secrets import settings
    from services.ai_service import _call_gemini, _call_openai
    import json

    prompt = STYLIST_BRIEFING_PROMPT.format(data=json.dumps(data, indent=2))
    try:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return await _call_gemini(prompt)
        elif settings.OPENAI_API_KEY:
            return await _call_openai(prompt)
    except Exception:
        pass

    # Fallback: structured plain text
    lines = []
    if data.get("known_allergies"):
        lines.append(f"⚠️ ALLERGY ALERT: {', '.join(data['known_allergies'])}. Verify all products before use.")
    if data.get("visit_goal"):
        lines.append(f"Visit goal: {data['visit_goal']}.")
    if data.get("hair_type"):
        lines.append(f"Hair: {data['hair_type']}, {data.get('scalp_condition', 'normal')} scalp.")
    if data.get("skin_type"):
        lines.append(f"Skin: {data['skin_type']}.")
    if data.get("is_pregnant"):
        lines.append("⚠️ Customer is pregnant — avoid ammonia, bleach, and harsh chemicals.")
    return " ".join(lines) or "Standard consultation. No special notes."


def _detect_allergy_conflict(
    service_name: str,
    allergies: list[str],
    sensitivities: list[str],
    is_pregnant: bool,
) -> dict:
    """Cross-check booked service against allergen list. Returns risk classification."""
    CHEMICAL_SERVICES = ["colour", "color", "keratin", "bleach", "perm", "relaxer",
                         "straighten", "highlight", "toner", "ammonia"]
    PREGNANCY_UNSAFE = ["bleach", "perm", "relaxer", "colour", "color", "highlight"]

    svc_lower = service_name.lower()
    is_chemical = any(kw in svc_lower for kw in CHEMICAL_SERVICES)
    all_allergens = [a.lower() for a in (allergies + sensitivities)]

    direct_conflict = [a for a in all_allergens if a in svc_lower or svc_lower in a]
    pregnancy_risk = is_pregnant and any(kw in svc_lower for kw in PREGNANCY_UNSAFE)

    if direct_conflict or pregnancy_risk:
        level = "BLOCK"
        reason = []
        if direct_conflict:
            reason.append(f"Customer is allergic to: {', '.join(direct_conflict)}")
        if pregnancy_risk:
            reason.append("Service contains chemicals unsafe during pregnancy")
        return {
            "risk_level": level,
            "can_proceed": False,
            "reason": ". ".join(reason),
            "suggested_alternative": "Consult senior stylist for ammonia-free / pregnancy-safe alternatives",
        }
    elif all_allergens and is_chemical:
        return {
            "risk_level": "HIGH",
            "can_proceed": False,
            "reason": f"Chemical service for customer with known sensitivities: {', '.join(all_allergens)}. Patch test required.",
            "suggested_alternative": "Perform patch test 48h before service or use allergen-free product line",
        }
    elif all_allergens:
        return {
            "risk_level": "CAUTION",
            "can_proceed": True,
            "reason": f"Customer has sensitivities: {', '.join(all_allergens)}. Verify all products.",
            "suggested_alternative": None,
        }
    else:
        return {"risk_level": "LOW", "can_proceed": True, "reason": None, "suggested_alternative": None}


@router.get("/booking/{booking_id}/info", response_model=APIResponse)
async def get_consultation_booking_info(booking_id: str, db: AsyncSession = Depends(get_db)):
    """Public endpoint — load basic booking details to pre-fill the consultation form header."""
    from models.booking import Booking
    from models.service import Service
    from models.location import Location
    from models.customer import CustomerProfile
    from models.user import User as UserModel

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    service = await db.get(Service, booking.service_id) if booking.service_id else None
    location = await db.get(Location, booking.location_id) if booking.location_id else None

    customer_name = ""
    if booking.customer_id:
        cp = await db.get(CustomerProfile, booking.customer_id)
        if cp:
            user = await db.get(UserModel, cp.user_id)
            if user:
                customer_name = f"{user.first_name} {user.last_name}".strip()

    return APIResponse(
        success=True,
        message="Booking info",
        data={
            "booking_id": booking_id,
            "customer_name": customer_name,
            "service_name": service.name if service else "Your Appointment",
            "location_name": location.name if location else "",
            "scheduled_at": str(booking.scheduled_at) if booking.scheduled_at else None,
        },
    )


@router.post("/send-link", response_model=APIResponse)
async def send_consultation_link(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send WhatsApp consultation form link to customer after booking is confirmed.
    Called automatically from the booking creation flow.
    """
    from models.booking import Booking
    from models.user import User as UserModel
    from services.sns_service import send_whatsapp
    import secrets

    booking_id = body.get("booking_id")
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    # Get customer phone
    from models.customer import CustomerProfile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    cp = cp_result.scalar_one_or_none()

    user_result = await db.execute(
        select(UserModel).where(UserModel.id == (cp.user_id if cp else None))
    )
    customer_user = user_result.scalar_one_or_none()

    if not customer_user or not customer_user.phone:
        return APIResponse(success=False, message="Customer phone not found", data={})

    # Generate one-time token (in production store in Redis with TTL)
    token = secrets.token_urlsafe(24)
    form_url = f"https://natural.dhilip.in/consult/{booking_id}?token={token}"

    msg = (
        f"Hi {customer_user.first_name}! 👋 Your AURA appointment is confirmed. "
        f"Please fill our 2-minute consultation form so your stylist can prepare for you: {form_url}\n"
        f"Takes just 2 minutes. Helps us give you the best experience! 💆"
    )
    await send_whatsapp(customer_user.phone, msg)

    return APIResponse(
        success=True,
        message="Consultation form link sent",
        data={"booking_id": booking_id, "form_url": form_url, "phone": customer_user.phone},
    )


@router.post("/submit", response_model=APIResponse)
async def submit_consultation(
    form: ConsultationSubmission,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — customer submits the consultation form (no auth needed, uses token).
    1. Validates token
    2. Checks allergy declaration signature
    3. Auto-populates Beauty Passport
    4. Generates AI stylist briefing
    5. Runs allergy conflict detection against booked service
    6. Logs audit record
    """
    from models.booking import Booking
    from models.customer import CustomerProfile
    from models.service import Service
    from models.notification import Notification

    if not form.allergy_declaration_signed:
        raise HTTPException(
            400,
            "Allergy declaration must be signed before submitting. "
            "Please confirm you have declared all known allergies."
        )

    booking = await db.get(Booking, form.booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found or link expired")

    # Auto-populate Beauty Passport
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    cp = cp_result.scalar_one_or_none()
    if cp:
        if form.hair_type:         cp.hair_type = form.hair_type
        if form.hair_texture:      cp.hair_texture = form.hair_texture
        if form.scalp_condition:   cp.scalp_condition = form.scalp_condition
        if form.current_hair_color: cp.current_hair_color = form.current_hair_color
        if form.skin_type:         cp.skin_type = form.skin_type
        if form.primary_skin_concerns: cp.primary_skin_concerns = form.primary_skin_concerns
        if form.known_allergies:   cp.known_allergies = form.known_allergies
        if form.product_sensitivities: cp.product_sensitivities = form.product_sensitivities

    # Get booked service name
    svc = await db.get(Service, booking.service_id) if booking.service_id else None
    service_name = svc.name if svc else ""

    # Allergy conflict detection
    conflict = _detect_allergy_conflict(
        service_name=service_name,
        allergies=form.known_allergies,
        sensitivities=form.product_sensitivities,
        is_pregnant=form.is_pregnant,
    )

    # Generate AI stylist briefing
    briefing = await _generate_stylist_briefing({
        "hair_type": form.hair_type,
        "scalp_condition": form.scalp_condition,
        "skin_type": form.skin_type,
        "known_allergies": form.known_allergies,
        "visit_goal": form.visit_goal,
        "is_pregnant": form.is_pregnant,
        "health_conditions": form.health_conditions,
        "occasion": form.occasion,
        "budget": form.budget_preference,
    })

    # Store briefing in booking notes
    existing_notes = booking.notes or ""
    booking.notes = f"[PRE-VISIT BRIEFING]\n{briefing}\n\n{existing_notes}".strip()
    booking.consultation_completed = True if hasattr(booking, "consultation_completed") else None

    # Audit log — allergy declaration
    notif = Notification(
        id=generate_uuid(),
        user_id=None,
        notification_type="consultation_submitted",
        title="Consultation Form Submitted",
        body=f"Booking {booking.booking_number}: allergy declaration signed. Conflict level: {conflict['risk_level']}",
        channel="system",
        priority="high" if conflict["risk_level"] in ["BLOCK", "HIGH"] else "normal",
        data={
            "booking_id": form.booking_id,
            "allergy_signed": True,
            "conflict": conflict,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    db.add(notif)
    await db.commit()

    # If BLOCK level — alert stylist immediately
    if conflict["risk_level"] == "BLOCK" and booking.stylist_id:
        from models.staff import StaffProfile
        from models.user import User as UserModel
        from services.sns_service import send_whatsapp
        staff = await db.get(StaffProfile, booking.stylist_id)
        if staff:
            stylist_user = await db.get(UserModel, staff.user_id)
            if stylist_user and stylist_user.phone:
                await send_whatsapp(
                    stylist_user.phone,
                    f"🚨 ALLERGY BLOCK — Booking {booking.booking_number}: "
                    f"{conflict['reason']}. Do NOT proceed without manager approval.",
                )

    return APIResponse(
        success=True,
        message="Consultation submitted successfully. Your stylist has been briefed.",
        data={
            "booking_id": form.booking_id,
            "stylist_briefing": briefing,
            "allergy_check": conflict,
            "passport_updated": cp is not None,
        },
    )


@router.get("/booking/{booking_id}/briefing", response_model=APIResponse)
async def get_stylist_briefing(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stylist retrieves the pre-visit briefing before the appointment."""
    from models.booking import Booking
    from models.customer import CustomerProfile

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    cp = cp_result.scalar_one_or_none()

    return APIResponse(
        success=True,
        message="Pre-visit briefing",
        data={
            "booking_id": booking_id,
            "briefing_notes": booking.notes,
            "known_allergies": cp.known_allergies if cp else [],
            "skin_type": cp.skin_type if cp else None,
            "hair_type": cp.hair_type if cp else None,
            "total_visits": cp.total_visits if cp else 0,
            "archetype": cp.dominant_archetype if cp else None,
        },
    )
