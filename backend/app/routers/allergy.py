"""Enhanced Allergy Checker — Idea 23: Ingredient-Level Safety Engine.

Domain logic:
  4-level risk classification: LOW / CAUTION / HIGH / BLOCK
  BLOCK is non-dismissable — requires manager override to proceed.
  Ingredient-level conflict detection (not just service-category level).
  Pregnancy-aware: separate unsafe-ingredient list for pregnant customers.
  Audit log every check — timestamped, stored in Notification table.
  Safe alternatives auto-suggested from approved substitute products.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, generate_uuid
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/allergy", tags=["Enhanced Allergy Checker"])


# ── Ingredient → allergen class mapping ──
INGREDIENT_ALLERGEN_MAP: dict[str, list[str]] = {
    "ammonia":         ["ammonia", "chemical_sensitivity", "strong_chemical"],
    "hydrogen peroxide": ["peroxide", "bleach", "oxidiser", "chemical_sensitivity"],
    "paraphenylenediamine": ["ppd", "hair_dye_allergy", "para-phenylenediamine"],
    "resorcinol":      ["resorcinol", "hair_dye_allergy"],
    "formaldehyde":    ["formaldehyde", "formalin", "keratin_allergy"],
    "thioglycolic acid": ["thioglycolate", "perm_allergy", "relaxer_allergy"],
    "sodium hydroxide": ["lye", "relaxer_allergy", "chemical_sensitivity"],
    "fragrance":       ["fragrance", "perfume", "parfum"],
    "lanolin":         ["lanolin", "wool_allergy"],
    "latex":           ["latex", "rubber_allergy"],
    "nickel":          ["nickel", "metal_allergy"],
    "methylisothiazolinone": ["mi", "preservative_allergy"],
    "cocamidopropyl betaine": ["cocamidopropyl", "surfactant_allergy"],
    "salicylic acid":  ["salicylate", "aspirin_allergy"],
    "glycolic acid":   ["aha_sensitivity", "acid_sensitivity"],
}

# ── Service → ingredient list ──
SERVICE_INGREDIENTS: dict[str, list[str]] = {
    "hair colour":  ["ammonia", "hydrogen peroxide", "paraphenylenediamine", "resorcinol"],
    "color":        ["ammonia", "hydrogen peroxide", "paraphenylenediamine", "resorcinol"],
    "bleach":       ["hydrogen peroxide", "ammonia", "persulfate"],
    "keratin":      ["formaldehyde", "thioglycolic acid", "fragrance"],
    "perm":         ["thioglycolic acid", "hydrogen peroxide", "fragrance"],
    "relaxer":      ["sodium hydroxide", "thioglycolic acid"],
    "straighten":   ["formaldehyde", "thioglycolic acid", "sodium hydroxide"],
    "highlight":    ["hydrogen peroxide", "paraphenylenediamine", "ammonia"],
    "facial":       ["glycolic acid", "salicylic acid", "fragrance", "lanolin"],
    "manicure":     ["formaldehyde", "toluene", "fragrance"],
    "pedicure":     ["formaldehyde", "toluene", "fragrance", "salicylic acid"],
    "head massage": ["fragrance", "lanolin", "mineral oil"],
    "hair spa":     ["fragrance", "glycolic acid"],
    "waxing":       ["fragrance", "resin", "latex"],
}

# ── Pregnancy-unsafe ingredients ──
PREGNANCY_UNSAFE: set[str] = {
    "ammonia", "hydrogen peroxide", "paraphenylenediamine", "resorcinol",
    "formaldehyde", "thioglycolic acid", "sodium hydroxide", "salicylic acid",
    "glycolic acid", "toluene",
}

# ── Safe alternative suggestions per service ──
SAFE_ALTERNATIVES: dict[str, str] = {
    "hair colour":  "Ammonia-free / PPD-free hair colour (e.g. Organic Colour Systems, Wella Pure)",
    "bleach":       "Balayage with low-peroxide cream bleach + patch test. Or tone-only with a deposit colour.",
    "keratin":      "Formaldehyde-free keratin (e.g. Brazilian Blowout Zero, Cezanne) — confirm with supplier SDS",
    "perm":         "Digital perm (heat-based, no thioglycolate) or wave set alternatives",
    "relaxer":      "Conditioning press or keratin smoothing without lye",
    "facial":       "Enzyme-based facial (papain/bromelain) — no AHA/BHA acids",
    "manicure":     "3-Free / 5-Free nail polish (no formaldehyde, toluene, DBP)",
    "waxing":       "Sugar waxing (no resin/latex) or threading for brow/lip shaping",
}


def _resolve_service_key(service_name: str) -> str:
    svc_lower = service_name.lower()
    for key in SERVICE_INGREDIENTS:
        if key in svc_lower or svc_lower in key:
            return key
    return ""


def _check_ingredient_conflicts(
    service_name: str,
    customer_allergens: list[str],
    is_pregnant: bool,
    is_breastfeeding: bool,
) -> dict:
    """Full ingredient-level conflict check with 4-level classification."""
    svc_key = _resolve_service_key(service_name)
    service_ingredients = SERVICE_INGREDIENTS.get(svc_key, [])
    allergen_lower = [a.lower().strip() for a in customer_allergens]

    # Build reverse: allergen tag → ingredient
    conflicting_ingredients = []
    matched_allergens = []
    for ingredient in service_ingredients:
        tags = INGREDIENT_ALLERGEN_MAP.get(ingredient, [ingredient])
        for allergen in allergen_lower:
            if allergen in tags or allergen in ingredient:
                conflicting_ingredients.append(ingredient)
                matched_allergens.append(allergen)
                break

    pregnancy_conflicts = [i for i in service_ingredients if i in PREGNANCY_UNSAFE] if (is_pregnant or is_breastfeeding) else []
    condition = "pregnancy" if is_pregnant else ("breastfeeding" if is_breastfeeding else None)

    # Classification
    if conflicting_ingredients or pregnancy_conflicts:
        reasons = []
        if conflicting_ingredients:
            reasons.append(
                f"Direct allergen conflict: {', '.join(set(conflicting_ingredients))} "
                f"matched against declared allergies: {', '.join(set(matched_allergens))}"
            )
        if pregnancy_conflicts:
            reasons.append(
                f"{condition.title()} safety: {', '.join(pregnancy_conflicts)} are contraindicated "
                f"during {condition}"
            )
        return {
            "risk_level": "BLOCK",
            "can_proceed": False,
            "is_dismissable": False,
            "conflicting_ingredients": list(set(conflicting_ingredients + pregnancy_conflicts)),
            "matched_allergens": list(set(matched_allergens)),
            "reason": " | ".join(reasons),
            "safe_alternative": SAFE_ALTERNATIVES.get(svc_key),
            "requires_manager_override": True,
        }

    if allergen_lower and service_ingredients:
        return {
            "risk_level": "HIGH",
            "can_proceed": False,
            "is_dismissable": False,
            "conflicting_ingredients": [],
            "matched_allergens": allergen_lower,
            "reason": (
                f"Customer has declared allergies ({', '.join(allergen_lower[:3])}) "
                f"and this service involves chemical ingredients. Patch test mandatory 48h prior."
            ),
            "safe_alternative": SAFE_ALTERNATIVES.get(svc_key),
            "requires_manager_override": False,
        }

    if allergen_lower:
        return {
            "risk_level": "CAUTION",
            "can_proceed": True,
            "is_dismissable": True,
            "conflicting_ingredients": [],
            "matched_allergens": allergen_lower,
            "reason": f"Customer has sensitivities ({', '.join(allergen_lower[:3])}). Verify all products before use.",
            "safe_alternative": None,
            "requires_manager_override": False,
        }

    return {
        "risk_level": "LOW",
        "can_proceed": True,
        "is_dismissable": True,
        "conflicting_ingredients": [],
        "matched_allergens": [],
        "reason": None,
        "safe_alternative": None,
        "requires_manager_override": False,
    }


class AllergyCheckRequest(BaseModel):
    booking_id: Optional[str] = None
    customer_id: Optional[str] = None
    service_name: str
    additional_allergens: list[str] = []
    is_pregnant: bool = False
    is_breastfeeding: bool = False


@router.post("/check", response_model=APIResponse)
async def check_allergy(
    body: AllergyCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Full ingredient-level allergy check for a customer + service combination.
    Can be called with booking_id (auto-fetches customer data) or standalone.
    Logs every check for audit trail. BLOCK level requires manager override.
    """
    from app.models.customer import CustomerProfile
    from app.models.booking import Booking
    from app.models.notification import Notification

    known_allergens: list[str] = list(body.additional_allergens)
    is_pregnant = body.is_pregnant
    is_breastfeeding = body.is_breastfeeding
    cp = None

    if body.booking_id:
        booking = await db.get(Booking, body.booking_id)
        if booking:
            cp_result = await db.execute(
                select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
            )
            cp = cp_result.scalar_one_or_none()

    elif body.customer_id:
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.id == body.customer_id)
        )
        cp = cp_result.scalar_one_or_none()

    if cp:
        known_allergens = list(set(known_allergens + (cp.known_allergies or []) + (cp.product_sensitivities or [])))
        # CustomerProfile pregnancy field
        if hasattr(cp, "is_pregnant") and cp.is_pregnant:
            is_pregnant = True

    result = _check_ingredient_conflicts(
        service_name=body.service_name,
        customer_allergens=known_allergens,
        is_pregnant=is_pregnant,
        is_breastfeeding=is_breastfeeding,
    )

    # Audit log
    notif = Notification(
        id=generate_uuid(),
        user_id=None,
        notification_type="allergy_check",
        title=f"Allergy Check: {result['risk_level']}",
        body=f"Service: {body.service_name} | Allergens: {', '.join(known_allergens[:5])} | Level: {result['risk_level']}",
        channel="system",
        priority="high" if result["risk_level"] in ["BLOCK", "HIGH"] else "normal",
        data={
            "booking_id": body.booking_id,
            "customer_id": body.customer_id,
            "service": body.service_name,
            "risk_level": result["risk_level"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    db.add(notif)
    await db.commit()

    return APIResponse(
        success=True,
        message=f"Allergy check complete — Risk level: {result['risk_level']}",
        data={
            "service": body.service_name,
            "service_ingredients": SERVICE_INGREDIENTS.get(_resolve_service_key(body.service_name), []),
            "customer_allergens": known_allergens,
            **result,
        },
    )


@router.post("/manager-override", response_model=APIResponse)
async def manager_override_allergy_block(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manager authorises proceeding despite BLOCK-level allergy risk.
    Requires manager/admin role. Creates audit trail with manager identity.
    """
    from app.models.notification import Notification
    from app.models.user import UserRole

    if current_user.role not in [UserRole.SALON_MANAGER, UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER]:
        raise HTTPException(403, "Only managers can override a BLOCK-level allergy alert")

    booking_id = body.get("booking_id")
    reason = body.get("reason", "Manager override — customer informed and consented")

    override_log = Notification(
        id=generate_uuid(),
        user_id=str(current_user.id),
        notification_type="allergy_override",
        title="BLOCK-Level Allergy Override Authorised",
        body=f"Booking {booking_id}: override by {current_user.first_name} ({current_user.role}). Reason: {reason}",
        channel="system",
        priority="critical",
        data={
            "booking_id": booking_id,
            "manager_id": str(current_user.id),
            "manager_name": current_user.first_name,
            "manager_role": str(current_user.role),
            "override_reason": reason,
            "overridden_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    db.add(override_log)
    await db.commit()

    return APIResponse(
        success=True,
        message="Override authorised. Ensure customer has signed the waiver.",
        data={
            "booking_id": booking_id,
            "override_authorised_by": current_user.first_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "waiver_required": True,
        },
    )


@router.get("/ingredient-info/{ingredient}", response_model=APIResponse)
async def get_ingredient_info(ingredient: str):
    """Return allergen class tags for a specific ingredient — used for stylist education."""
    ingredient_lower = ingredient.lower()
    tags = INGREDIENT_ALLERGEN_MAP.get(ingredient_lower)
    if not tags:
        # Fuzzy match
        for key, val in INGREDIENT_ALLERGEN_MAP.items():
            if ingredient_lower in key or key in ingredient_lower:
                tags = val
                ingredient_lower = key
                break

    return APIResponse(
        success=True,
        message="Ingredient information",
        data={
            "ingredient": ingredient_lower,
            "allergen_classes": tags or [],
            "pregnancy_unsafe": ingredient_lower in PREGNANCY_UNSAFE,
            "found": tags is not None,
        },
    )


@router.get("/service/{service_name}/ingredients", response_model=APIResponse)
async def get_service_ingredients(service_name: str):
    """List all ingredients used in a service — for customer transparency."""
    svc_key = _resolve_service_key(service_name)
    ingredients = SERVICE_INGREDIENTS.get(svc_key, [])
    allergen_classes = {}
    for ing in ingredients:
        allergen_classes[ing] = INGREDIENT_ALLERGEN_MAP.get(ing, [ing])

    return APIResponse(
        success=True,
        message="Service ingredient profile",
        data={
            "service": service_name,
            "matched_key": svc_key or "unknown",
            "ingredients": ingredients,
            "allergen_classes": allergen_classes,
            "pregnancy_unsafe_ingredients": [i for i in ingredients if i in PREGNANCY_UNSAFE],
            "safe_alternative": SAFE_ALTERNATIVES.get(svc_key),
        },
    )
