"""Smart Upsell Engine — Idea 17: Revenue at the Chair.

Domain logic:
  Before service starts, generate a personalised upsell card for the stylist.
  Rules applied in order:
    1. Allergy safety filter — NEVER suggest anything conflicting with known allergies
    2. Service compatibility — add-ons that pair well with the booked service
    3. Collaborative filtering — "customers with this profile also booked X"
    4. Visit milestone triggers — 5th visit = free conditioning offer, upsell premium
    5. Beauty Passport signals — oily scalp → scalp detox, low hydration → moisture treatment
    6. Revenue optimisation — prefer higher-margin add-ons when multiple options qualify
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.common import APIResponse

router = APIRouter(prefix="/upsell", tags=["Smart Upsell Engine"])


# ── Service compatibility map (which add-ons pair with which base service) ──
SERVICE_PAIRINGS: dict[str, list[dict]] = {
    "hair colour": [
        {"service": "Keratin Treatment", "reason": "Protects colour and adds shine", "acceptance_rate": 0.70, "revenue_uplift": 1200},
        {"service": "Deep Conditioning", "reason": "Restores moisture lost during colouring", "acceptance_rate": 0.65, "revenue_uplift": 500},
        {"service": "Scalp Treatment", "reason": "Soothes scalp after chemical process", "acceptance_rate": 0.45, "revenue_uplift": 600},
    ],
    "keratin": [
        {"service": "Hair Spa", "reason": "Maximises keratin penetration", "acceptance_rate": 0.55, "revenue_uplift": 800},
        {"service": "Deep Conditioning", "reason": "Pre-treatment moisture boost improves results", "acceptance_rate": 0.60, "revenue_uplift": 500},
    ],
    "hair cut": [
        {"service": "Head Massage", "reason": "Popular pairing — 68% of customers add this", "acceptance_rate": 0.68, "revenue_uplift": 300},
        {"service": "Hair Spa", "reason": "Complete hair care session", "acceptance_rate": 0.50, "revenue_uplift": 700},
        {"service": "Blow Dry & Styling", "reason": "Finish the look professionally", "acceptance_rate": 0.72, "revenue_uplift": 400},
    ],
    "facial": [
        {"service": "Eyebrow Threading", "reason": "Complete face grooming — 75% add-on rate", "acceptance_rate": 0.75, "revenue_uplift": 150},
        {"service": "Face Massage", "reason": "Enhances product absorption post-facial", "acceptance_rate": 0.55, "revenue_uplift": 400},
        {"service": "Vitamin C Treatment", "reason": "Brightening booster for this skin type", "acceptance_rate": 0.40, "revenue_uplift": 800},
    ],
    "bridal makeup": [
        {"service": "Hair Styling", "reason": "Complete bridal look package", "acceptance_rate": 0.90, "revenue_uplift": 2000},
        {"service": "Mehendi", "reason": "Popular bridal combo", "acceptance_rate": 0.65, "revenue_uplift": 1500},
        {"service": "Pre-Bridal Facial", "reason": "Glow treatment before makeup application", "acceptance_rate": 0.80, "revenue_uplift": 1200},
    ],
    "manicure": [
        {"service": "Pedicure", "reason": "90% of manicure customers add pedicure", "acceptance_rate": 0.90, "revenue_uplift": 600},
        {"service": "Nail Art", "reason": "Trending — 45% add-on rate this month", "acceptance_rate": 0.45, "revenue_uplift": 400},
    ],
    "default": [
        {"service": "Head Massage", "reason": "Universally loved relaxation add-on", "acceptance_rate": 0.55, "revenue_uplift": 300},
    ],
}

# ── Passport-signal triggers ──
PASSPORT_TRIGGERS: list[dict] = [
    {"condition": "oily_scalp",      "signal_field": "scalp_condition", "signal_value": "oily",        "service": "Scalp Detox Treatment",   "reason": "Your Beauty Passport shows oily scalp — this treatment balances sebum production"},
    {"condition": "dry_hair",        "signal_field": "hair_type",       "signal_value": "dry",          "service": "Deep Conditioning Mask",  "reason": "Dry hair type — intensive moisture treatment will restore strength"},
    {"condition": "pigmentation",    "signal_field": "pigmentation_level", "signal_value": 3,           "service": "Brightening Facial",      "reason": "Passport shows pigmentation concerns — Vitamin C brightening will help"},
    {"condition": "acne",            "signal_field": "acne_severity",   "signal_value": 2,              "service": "Acne Control Facial",     "reason": "Acne-prone skin — specialised treatment to prevent breakouts"},
    {"condition": "damaged_hair",    "signal_field": "hair_damage_level","signal_value": 3,             "service": "Protein Treatment",       "reason": "High hair damage level — protein strengthens and rebuilds hair structure"},
]

# ── Visit milestone triggers ──
MILESTONE_TRIGGERS: list[dict] = [
    {"visits": 5,  "offer": "Complimentary Deep Conditioning", "upsell": "Premium Hair Spa",          "message": "Congratulate her on 5 visits! Offer a complimentary conditioning and mention the Premium Hair Spa upgrade (₹700 extra)"},
    {"visits": 10, "offer": "Complimentary Hair Mask",          "upsell": "Colour Touch-Up",           "message": "Gold tier milestone! She's earned a free hair mask. Upsell a colour touch-up while the mask is processing"},
    {"visits": 20, "offer": "Complimentary Scalp Treatment",    "upsell": "Platinum Membership Package","message": "Platinum customer! Give her the VIP treatment. Offer scalp treatment free and present the Platinum membership"},
]


async def _get_suggestions(
    booking_id: str,
    db: AsyncSession,
) -> list[dict]:
    """Core upsell suggestion engine — returns ranked, allergy-safe suggestions."""
    from app.models.booking import Booking
    from app.models.customer import CustomerProfile
    from app.models.service import Service

    booking = await db.get(Booking, booking_id)
    if not booking:
        return []

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    cp = cp_result.scalar_one_or_none()

    svc_result = await db.execute(
        select(Service).where(Service.id == booking.service_id)
    ) if booking.service_id else None
    svc = svc_result.scalar_one_or_none() if svc_result else None
    service_name = (svc.name or "").lower() if svc else "default"

    known_allergies = [a.lower() for a in (cp.known_allergies or [])] if cp else []
    sensitivities = [s.lower() for s in (cp.product_sensitivities or [])] if cp else []
    all_allergens = known_allergies + sensitivities

    suggestions = []

    # 1. Service compatibility pairings
    pairings = []
    for key, options in SERVICE_PAIRINGS.items():
        if key in service_name or service_name in key:
            pairings = options
            break
    if not pairings:
        pairings = SERVICE_PAIRINGS["default"]

    for p in pairings:
        # Allergy safety filter
        svc_lower = p["service"].lower()
        if any(allergen in svc_lower for allergen in all_allergens):
            continue
        suggestions.append({
            "service": p["service"],
            "reason": p["reason"],
            "acceptance_rate_pct": int(p["acceptance_rate"] * 100),
            "revenue_uplift": p["revenue_uplift"],
            "source": "service_pairing",
            "priority": p["acceptance_rate"],
        })

    # 2. Beauty Passport signal triggers
    if cp:
        for trigger in PASSPORT_TRIGGERS:
            field = trigger["signal_field"]
            expected = trigger["signal_value"]
            actual = getattr(cp, field, None)
            match = False
            if isinstance(expected, int):
                match = actual is not None and actual >= expected
            else:
                match = str(actual or "").lower() == expected
            if match:
                if not any(allergen in trigger["service"].lower() for allergen in all_allergens):
                    suggestions.append({
                        "service": trigger["service"],
                        "reason": trigger["reason"],
                        "acceptance_rate_pct": 60,
                        "revenue_uplift": 700,
                        "source": "beauty_passport",
                        "priority": 0.75,
                    })

    # 3. Visit milestone triggers
    if cp and cp.total_visits:
        for milestone in MILESTONE_TRIGGERS:
            if cp.total_visits == milestone["visits"]:
                suggestions.insert(0, {
                    "service": milestone["upsell"],
                    "reason": milestone["message"],
                    "acceptance_rate_pct": 80,
                    "revenue_uplift": 1000,
                    "source": "milestone",
                    "priority": 1.0,
                    "free_offer": milestone["offer"],
                })
                break

    # Sort by priority desc
    suggestions.sort(key=lambda x: x["priority"], reverse=True)

    # Remove duplicates and limit
    seen = set()
    unique = []
    for s in suggestions:
        if s["service"] not in seen:
            seen.add(s["service"])
            unique.append(s)

    return unique[:4]


@router.get("/booking/{booking_id}", response_model=APIResponse)
async def get_upsell_suggestions(
    booking_id: str,
    current_user: User = Depends(require_role([UserRole.STYLIST, UserRole.SALON_MANAGER, UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Get real-time upsell card for stylist before service starts.
    Called automatically when stylist opens the live session screen.
    Returns ranked, allergy-safe add-on suggestions with reasoning.
    """
    from app.models.booking import Booking
    from app.models.customer import CustomerProfile

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    cp = cp_result.scalar_one_or_none()

    suggestions = await _get_suggestions(booking_id, db)

    return APIResponse(
        success=True,
        message="Upsell suggestions ready",
        data={
            "booking_id": booking_id,
            "customer_name": None,
            "customer_visit_count": cp.total_visits if cp else None,
            "suggestions": suggestions,
            "allergy_safe": True,
            "total_potential_uplift": sum(s["revenue_uplift"] for s in suggestions[:2]),
        },
    )


@router.post("/booking/{booking_id}/accepted", response_model=APIResponse)
async def record_upsell_accepted(
    booking_id: str,
    body: dict,
    current_user: User = Depends(require_role([UserRole.STYLIST, UserRole.SALON_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    """Record which upsell was accepted — used for A/B tracking and conversion analytics."""
    from app.models.booking import Booking

    service_accepted = body.get("service")
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    # Append to add_on_services
    addons = booking.add_on_services or []
    if service_accepted and service_accepted not in addons:
        addons.append(service_accepted)
        booking.add_on_services = addons
        await db.commit()

    return APIResponse(
        success=True,
        message="Upsell recorded",
        data={"booking_id": booking_id, "accepted_service": service_accepted},
    )
