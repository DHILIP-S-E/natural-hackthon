"""Track 3: Personalization — 10 agents for beauty passport, diagnosis, homecare,
allergy safety, next-best-service, virtual try-on, journey planning, climate
adjustments, loyalty offers, and occasion planning.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select, func, desc, and_, extract, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role, check_customer_ownership
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.booking import Booking, BookingStatus
from app.models.service import Service, SOP
from app.models.soulskin import SoulskinSession
from app.models.mood import MoodDetection
from app.models.digital_twin import DigitalBeautyTwin
from app.models.homecare import HomecarePlan
from app.models.journey import BeautyJourneyPlan
from app.models.climate import ClimateRecommendation
from app.models.ar_mirror import ARMirrorSession, MirrorSessionType, MirrorInitiator
from app.models.feedback import CustomerFeedback, Sentiment
from app.models.session import ServiceSession, SessionStatus
from app.models.staff import StaffProfile
from app.models.loyalty import LoyaltyProgram, PersonalizedOffer
from app.models.location import Location
from app.schemas.common import APIResponse
from app.agents import AgentAction, register_agent


# ─────────────────────────────────────────────────────────────────────────────
# 24. beauty_passport_full  (PS-03.01)
# ─────────────────────────────────────────────────────────────────────────────

async def beauty_passport_full_handler(
    customer_id: str = Query(..., description="Customer profile ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Return the complete beauty passport for a customer."""
    await check_customer_ownership(user, customer_id, db)

    # ── Core profile ──
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Latest SOULSKIN session + history ──
    ss_result = await db.execute(
        select(SoulskinSession)
        .where(SoulskinSession.customer_id == customer_id)
        .order_by(desc(SoulskinSession.created_at))
        .limit(5)
    )
    soulskin_sessions = ss_result.scalars().all()
    soulskin_current = soulskin_sessions[0] if soulskin_sessions else None

    # ── Last 5 completed services with outcomes ──
    bk_result = await db.execute(
        select(Booking, Service, ServiceSession)
        .join(Service, Service.id == Booking.service_id)
        .outerjoin(ServiceSession, ServiceSession.booking_id == Booking.id)
        .where(
            Booking.customer_id == customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(desc(Booking.scheduled_at))
        .limit(5)
    )
    recent_services = bk_result.all()

    last_services = []
    for bk, svc, sess in recent_services:
        last_services.append({
            "booking_id": bk.id,
            "service_name": svc.name,
            "category": svc.category,
            "date": str(bk.scheduled_at) if bk.scheduled_at else None,
            "final_price": float(bk.final_price) if bk.final_price else None,
            "quality_score": float(sess.quality_score) if sess and sess.quality_score else None,
            "sop_compliance_pct": float(sess.sop_compliance_pct) if sess and sess.sop_compliance_pct else None,
            "archetype_applied": sess.archetype_applied if sess else None,
        })

    # ── Preferred stylist info ──
    stylist_info = None
    if profile.preferred_stylist_id:
        st_result = await db.execute(
            select(StaffProfile, User)
            .join(User, User.id == StaffProfile.user_id)
            .where(StaffProfile.id == profile.preferred_stylist_id)
        )
        st_row = st_result.first()
        if st_row:
            sp, su = st_row
            stylist_info = {
                "id": sp.id,
                "name": f"{su.first_name} {su.last_name}",
                "specializations": sp.specializations,
                "skill_level": enum_val(sp.skill_level) if sp.skill_level else None,
                "rating": float(sp.current_rating) if sp.current_rating else None,
                "soulskin_certified": sp.soulskin_certified,
            }

    passport = {
        "customer_id": profile.id,
        "hair_profile": {
            "type": profile.hair_type,
            "texture": profile.hair_texture,
            "porosity": profile.hair_porosity,
            "density": profile.hair_density,
            "damage_level": profile.hair_damage_level,
            "natural_color": profile.natural_hair_color,
            "current_color": profile.current_hair_color,
            "last_color_date": str(profile.last_color_date) if profile.last_color_date else None,
            "scalp_condition": profile.scalp_condition,
            "chemical_history": profile.chemical_history,
        },
        "skin_profile": {
            "type": profile.skin_type,
            "tone": profile.skin_tone,
            "undertone": profile.undertone,
            "concerns": profile.primary_skin_concerns,
            "sensitivity": profile.skin_sensitivity,
            "acne_severity": profile.acne_severity,
            "pigmentation_level": profile.pigmentation_level,
            "wrinkle_score": profile.wrinkle_score,
            "hydration": profile.hydration_estimate,
        },
        "soulskin": {
            "dominant_archetype": profile.dominant_archetype,
            "current_session_archetype": soulskin_current.archetype if soulskin_current else None,
            "soul_reading": soulskin_current.soul_reading if soulskin_current else None,
            "archetype_history": profile.archetype_history,
            "history": [
                {
                    "session_id": s.id,
                    "archetype": s.archetype,
                    "date": str(s.created_at),
                    "song": s.question_1_song,
                    "colour": s.question_2_colour,
                    "word": s.question_3_word,
                }
                for s in soulskin_sessions
            ],
        },
        "known_allergies": profile.known_allergies,
        "product_sensitivities": profile.product_sensitivities,
        "lifestyle": {
            "stress_level": profile.stress_level,
            "diet_type": profile.diet_type,
            "climate_type": profile.climate_type,
            "city": profile.city,
            "sun_exposure": profile.sun_exposure,
            "occupation": profile.occupation_type,
            "water_quality": profile.water_quality,
            "sleep_quality": profile.sleep_quality,
            "hydration_habit": profile.hydration_habit,
        },
        "beauty_score": profile.beauty_score,
        "passport_completeness": profile.passport_completeness,
        "total_visits": profile.total_visits,
        "lifetime_value": float(profile.lifetime_value) if profile.lifetime_value else 0,
        "last_5_services": last_services,
        "preferred_stylist": stylist_info,
        "beauty_goals": {
            "primary_goal": profile.primary_goal,
            "timeline_weeks": profile.goal_timeline_weeks,
            "progress_pct": profile.goal_progress_pct,
            "notes": profile.goal_notes,
        },
    }

    return APIResponse(success=True, data=passport)


beauty_passport_full_agent = register_agent(AgentAction(
    name="beauty_passport_full",
    description="Returns the COMPLETE beauty passport: hair, skin, SOULSKIN, allergies, lifestyle, recent services, preferred stylist",
    track="personalization",
    feature="passport",
    method="get",
    path="/agents/track3/passport/full",
    handler=beauty_passport_full_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.01"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 25. ai_hair_skin_diagnosis  (PS-03.02)
# ─────────────────────────────────────────────────────────────────────────────

async def ai_hair_skin_diagnosis_handler(
    customer_id: str = Query(..., description="Customer profile ID"),
    image_analysis: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Compute objective hair/skin diagnosis from profile data and optional image analysis."""
    await check_customer_ownership(user, customer_id, db)

    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Hair health scoring (0-100) ──
    hair_score = 100
    damage = profile.hair_damage_level or 0
    hair_score -= damage * 10  # 0-10 damage scale

    if profile.scalp_condition and profile.scalp_condition.lower() in ("dry", "flaky", "oily", "irritated"):
        hair_score -= 10
    if profile.hair_porosity and profile.hair_porosity.lower() == "high":
        hair_score -= 10
    if profile.chemical_history:
        treatments = profile.chemical_history.get("treatments", [])
        if len(treatments) > 3:
            hair_score -= 5 * min(len(treatments) - 3, 4)
    hair_score = max(0, min(100, hair_score))

    # ── Skin health scoring (0-100) ──
    skin_score = 100
    acne = profile.acne_severity or 0
    skin_score -= acne * 8
    pigmentation = profile.pigmentation_level or 0
    skin_score -= pigmentation * 5
    wrinkles = profile.wrinkle_score or 0
    skin_score -= wrinkles * 4
    if profile.skin_sensitivity and profile.skin_sensitivity.lower() in ("high", "very_high"):
        skin_score -= 10
    if profile.hydration_estimate and profile.hydration_estimate.lower() in ("low", "very_low"):
        skin_score -= 10
    skin_score = max(0, min(100, skin_score))

    # If image analysis results provided, blend them in
    if image_analysis:
        img_hair = image_analysis.get("hair_health_score")
        img_skin = image_analysis.get("skin_health_score")
        if img_hair is not None:
            hair_score = int(hair_score * 0.5 + float(img_hair) * 0.5)
        if img_skin is not None:
            skin_score = int(skin_score * 0.5 + float(img_skin) * 0.5)

    # ── Damage severity and urgency ──
    damage_severity = "none"
    if damage >= 8:
        damage_severity = "critical"
    elif damage >= 6:
        damage_severity = "severe"
    elif damage >= 4:
        damage_severity = "moderate"
    elif damage >= 2:
        damage_severity = "mild"

    combined_score = (hair_score + skin_score) / 2
    treatment_urgency = "low"
    if combined_score < 40:
        treatment_urgency = "critical"
    elif combined_score < 55:
        treatment_urgency = "high"
    elif combined_score < 70:
        treatment_urgency = "medium"

    # ── Key concerns ──
    key_concerns = []
    if damage >= 4:
        key_concerns.append(f"Hair damage level {damage}/10")
    if profile.scalp_condition and profile.scalp_condition.lower() != "healthy":
        key_concerns.append(f"Scalp condition: {profile.scalp_condition}")
    if profile.hair_porosity and profile.hair_porosity.lower() == "high":
        key_concerns.append("High hair porosity — moisture retention issues")
    if acne >= 3:
        key_concerns.append(f"Acne severity {acne}/10")
    if profile.primary_skin_concerns:
        for c in profile.primary_skin_concerns[:3]:
            key_concerns.append(f"Skin concern: {c}")
    if profile.skin_sensitivity and profile.skin_sensitivity.lower() in ("high", "very_high"):
        key_concerns.append("High skin sensitivity — patch test strongly recommended")
    if profile.stress_level and profile.stress_level.lower() in ("high", "very_high"):
        key_concerns.append("High stress — impacts hair fall and skin health")

    # ── Recommended treatments from service catalog ──
    treatment_categories = []
    if damage >= 4:
        treatment_categories.extend(["hair treatment", "hair spa", "hair repair"])
    if acne >= 3:
        treatment_categories.extend(["facial", "skin treatment", "cleanup"])
    if profile.scalp_condition and profile.scalp_condition.lower() != "healthy":
        treatment_categories.extend(["scalp treatment", "hair spa"])
    if profile.primary_skin_concerns:
        treatment_categories.extend(["facial", "skin treatment"])

    recommended_treatments = []
    if treatment_categories:
        svc_result = await db.execute(
            select(Service)
            .where(
                Service.is_active == True,
                func.lower(Service.category).in_([c.lower() for c in set(treatment_categories)]),
            )
            .order_by(Service.base_price)
            .limit(5)
        )
        services = svc_result.scalars().all()
        for svc in services:
            recommended_treatments.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "duration_minutes": svc.duration_minutes,
                "price": float(svc.base_price),
            })

    diagnosis = {
        "customer_id": customer_id,
        "hair_health_score": hair_score,
        "skin_health_score": skin_score,
        "combined_score": round(combined_score, 1),
        "damage_severity": damage_severity,
        "treatment_urgency": treatment_urgency,
        "key_concerns": key_concerns,
        "recommended_treatments": recommended_treatments,
        "diagnosis_date": str(datetime.now(timezone.utc).date()),
        "data_sources": {
            "profile_data": True,
            "image_analysis": image_analysis is not None,
        },
    }

    return APIResponse(success=True, data=diagnosis)


ai_hair_skin_diagnosis_agent = register_agent(AgentAction(
    name="ai_hair_skin_diagnosis",
    description="AI-powered hair & skin diagnosis scoring (0-100) with treatment urgency and recommendations",
    track="personalization",
    feature="diagnosis",
    method="get",
    path="/agents/track3/diagnosis/hair-skin",
    handler=ai_hair_skin_diagnosis_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.02"],
    requires_ai=True,
))


# ─────────────────────────────────────────────────────────────────────────────
# 26. generate_homecare_plan  (PS-03.03)
# ─────────────────────────────────────────────────────────────────────────────

async def generate_homecare_plan_handler(
    customer_id: str = Query(...),
    booking_id: str = Query(...),
    service_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Generate a personalized homecare plan after a service session."""

    # ── Validate customer ──
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Validate booking ──
    bk_result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.customer_id == customer_id)
    )
    booking = bk_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found for this customer")

    # ── Validate service ──
    svc_result = await db.execute(select(Service).where(Service.id == service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # ── Get climate data for customer's city ──
    climate_data = None
    if profile.city:
        clm_result = await db.execute(
            select(ClimateRecommendation)
            .where(ClimateRecommendation.city == profile.city)
            .order_by(desc(ClimateRecommendation.date_for))
            .limit(1)
        )
        climate_data = clm_result.scalar_one_or_none()

    # ── Get latest SOULSKIN archetype ──
    ss_result = await db.execute(
        select(SoulskinSession)
        .where(SoulskinSession.customer_id == customer_id)
        .order_by(desc(SoulskinSession.created_at))
        .limit(1)
    )
    soulskin = ss_result.scalar_one_or_none()
    archetype = soulskin.archetype if soulskin else profile.dominant_archetype

    # ── Build the homecare plan ──
    is_chemical = service.is_chemical
    hair_type_lower = (profile.hair_type or "normal").lower()
    skin_type_lower = (profile.skin_type or "normal").lower()

    # Daily routine
    daily_routine = []
    if is_chemical:
        daily_routine.append("Use sulfate-free shampoo to protect chemical treatment")
        daily_routine.append("Apply leave-in conditioner on damp hair")
    else:
        daily_routine.append(f"Use a gentle shampoo suited for {hair_type_lower} hair")
    if skin_type_lower in ("oily", "combination"):
        daily_routine.append("Use oil-free moisturizer morning and night")
        daily_routine.append("Apply gel-based sunscreen SPF 30+")
    elif skin_type_lower == "dry":
        daily_routine.append("Apply rich moisturizing cream twice daily")
        daily_routine.append("Use cream-based sunscreen SPF 30+")
    else:
        daily_routine.append("Moisturize daily and apply SPF 30+ sunscreen")

    # Weekly routine
    weekly_routine = []
    weekly_routine.append(f"Deep conditioning mask for {hair_type_lower} hair — once a week")
    if service.category and "color" in service.category.lower():
        weekly_routine.append("Color-protecting hair mask — twice a week")
    if skin_type_lower in ("oily", "combination"):
        weekly_routine.append("Clay face mask — once a week")
    elif skin_type_lower == "dry":
        weekly_routine.append("Hydrating sheet mask — twice a week")
    else:
        weekly_routine.append("Exfoliate gently — once a week")

    # Products to use / avoid
    products_to_use = []
    products_to_avoid = []
    if is_chemical:
        products_to_use.extend(["Sulfate-free shampoo", "Color-safe conditioner", "Heat protectant spray"])
        products_to_avoid.extend(["Clarifying shampoos", "Products with alcohol", "Harsh sulfates"])
    else:
        products_to_use.extend([f"Shampoo formulated for {hair_type_lower} hair", "Lightweight conditioner"])
    if profile.known_allergies:
        for allergen in profile.known_allergies:
            products_to_avoid.append(f"Products containing {allergen}")

    # Climate adjustments
    climate_adjustments = []
    if climate_data:
        temp = float(climate_data.temperature_celsius) if climate_data.temperature_celsius else None
        humidity = float(climate_data.humidity_pct) if climate_data.humidity_pct else None
        uv = float(climate_data.uv_index) if climate_data.uv_index else None

        if temp and temp > 35:
            climate_adjustments.append("High temperature: wash hair more frequently, use cooling scalp tonic")
        if humidity and humidity > 75:
            climate_adjustments.append("High humidity: use anti-frizz serum, lightweight products")
        elif humidity and humidity < 30:
            climate_adjustments.append("Low humidity: extra moisturizing, avoid blow-drying")
        if uv and uv > 6:
            climate_adjustments.append("High UV index: wear hat outdoors, use UV-protecting hair spray")
        if climate_data.hair_recommendations:
            climate_adjustments.append(f"Hair tip: {climate_data.hair_recommendations}")
        if climate_data.skin_recommendations:
            climate_adjustments.append(f"Skin tip: {climate_data.skin_recommendations}")

    # Archetype rituals
    archetype_rituals = []
    archetype_map = {
        "fire": ["Energizing scalp massage with peppermint oil", "Bright-colored nail art or bold lip color touch-up"],
        "earth": ["Grounding scalp massage with cedarwood oil", "Natural ingredient masks (honey, avocado)"],
        "water": ["Calming hair oil ritual before bed", "Hydrating facial mist throughout the day"],
        "air": ["Lightweight styling with volume-boosting products", "Quick refreshing face mist routine"],
        "ether": ["Meditative brushing ritual — 100 strokes before bed", "Crystal-infused facial mist"],
    }
    if archetype and archetype.lower() in archetype_map:
        archetype_rituals = archetype_map[archetype.lower()]

    # Dos and donts
    dos = [
        "Drink at least 8 glasses of water daily",
        "Sleep 7-8 hours for optimal hair and skin repair",
        "Pat hair dry gently — never rub vigorously",
    ]
    donts = [
        "Avoid excessive heat styling for 48 hours post-treatment",
        "Do not scratch or pick at the scalp",
    ]
    if is_chemical:
        dos.append("Wait 48 hours before first wash after chemical treatment")
        donts.append("Avoid chlorinated pools for 2 weeks")

    # Next visit suggestion: 4 weeks standard, 3 weeks for chemical
    next_visit_weeks = 3 if is_chemical else 4
    next_visit_date = date.today() + timedelta(weeks=next_visit_weeks)

    # ── Persist the plan ──
    plan = HomecarePlan(
        customer_id=customer_id,
        booking_id=booking_id,
        soulskin_archetype=archetype,
        generated_at=datetime.now(timezone.utc),
        plan_duration_weeks=next_visit_weeks,
        hair_routine={"daily": daily_routine, "weekly": weekly_routine},
        skin_routine={"daily": [r for r in daily_routine if "skin" in r.lower() or "moistur" in r.lower() or "sunscreen" in r.lower() or "SPF" in r],
                      "weekly": [r for r in weekly_routine if "face" in r.lower() or "mask" in r.lower() or "exfol" in r.lower() or "sheet" in r.lower()]},
        climate_adjustments={"tips": climate_adjustments} if climate_adjustments else None,
        archetype_rituals={"rituals": archetype_rituals} if archetype_rituals else None,
        product_recommendations={"use": products_to_use, "avoid": products_to_avoid},
        dos=dos,
        donts=donts,
        next_visit_recommendation=f"Recommended return in {next_visit_weeks} weeks for {service.name} maintenance",
        next_visit_suggested_date=next_visit_date,
    )
    db.add(plan)
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "plan_id": plan.id,
            "customer_id": customer_id,
            "service_done": service.name,
            "archetype": archetype,
            "daily_routine": daily_routine,
            "weekly_routine": weekly_routine,
            "products_to_use": products_to_use,
            "products_to_avoid": products_to_avoid,
            "climate_adjustments": climate_adjustments,
            "archetype_rituals": archetype_rituals,
            "dos": dos,
            "donts": donts,
            "next_visit_date": str(next_visit_date),
            "next_visit_weeks": next_visit_weeks,
        },
    )


generate_homecare_plan_agent = register_agent(AgentAction(
    name="generate_homecare_plan",
    description="Generate personalized homecare plan post-service with climate + archetype adjustments",
    track="personalization",
    feature="homecare",
    method="post",
    path="/agents/track3/homecare/generate",
    handler=generate_homecare_plan_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-03.03"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 27. allergy_safety_check  (PS-03.04)
# ─────────────────────────────────────────────────────────────────────────────

async def allergy_safety_check_handler(
    customer_id: str = Query(...),
    service_id: str = Query(...),
    products: list[str] = Query(default=[], description="List of product names to check"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Check customer allergies against products/service ingredients."""

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    svc_result = await db.execute(select(Service).where(Service.id == service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    customer_allergies = [a.lower().strip() for a in (profile.known_allergies or [])]
    customer_sensitivities = [s.lower().strip() for s in (profile.product_sensitivities or [])]

    # Get SOP products if available
    sop_products = []
    if service.sop_id:
        sop_result = await db.execute(select(SOP).where(SOP.id == service.sop_id))
        sop = sop_result.scalar_one_or_none()
        if sop and sop.products_required:
            sop_products = sop.products_required

    all_products = list(set(products + sop_products))

    warnings = []
    safe = True

    for product in all_products:
        product_lower = product.lower()
        for allergen in customer_allergies:
            if allergen in product_lower or product_lower in allergen:
                safe = False
                warnings.append({
                    "product": product,
                    "allergen_match": allergen,
                    "severity": "high",
                    "source": "known_allergy",
                    "alternative_product": f"Hypoallergenic alternative for {product} (allergen-free variant)",
                })
        for sensitivity in customer_sensitivities:
            if sensitivity in product_lower or product_lower in sensitivity:
                warnings.append({
                    "product": product,
                    "allergen_match": sensitivity,
                    "severity": "medium",
                    "source": "product_sensitivity",
                    "alternative_product": f"Gentle/sensitive-skin variant of {product}",
                })

    # Chemical service extra checks
    if service.is_chemical:
        if not profile.patch_tested_on:
            safe = False
            warnings.append({
                "product": "Chemical service",
                "allergen_match": "No patch test on record",
                "severity": "critical",
                "source": "patch_test_missing",
                "alternative_product": "Conduct patch test 48 hours before service",
            })
        elif profile.patch_test_result and profile.patch_test_result.lower() in ("failed", "reaction"):
            safe = False
            warnings.append({
                "product": "Chemical service",
                "allergen_match": f"Previous patch test result: {profile.patch_test_result}",
                "severity": "critical",
                "source": "patch_test_failed",
                "alternative_product": "Use ammonia-free / organic alternatives or avoid chemical services",
            })

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "service_id": service_id,
            "service_name": service.name,
            "is_chemical_service": service.is_chemical,
            "safe": safe,
            "total_products_checked": len(all_products),
            "warnings_count": len(warnings),
            "warnings": warnings,
        },
    )


allergy_safety_check_agent = register_agent(AgentAction(
    name="allergy_safety_check",
    description="Check customer allergies / sensitivities against products and service ingredients",
    track="personalization",
    feature="safety",
    method="post",
    path="/agents/track3/safety/allergy-check",
    handler=allergy_safety_check_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-03.04"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 28. next_best_service  (PS-03.05)
# ─────────────────────────────────────────────────────────────────────────────

async def next_best_service_handler(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Analyze customer history and return top 3 next-best-service recommendations."""
    await check_customer_ownership(user, customer_id, db)

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Last booking and frequency ──
    bk_result = await db.execute(
        select(Booking, Service)
        .join(Service, Service.id == Booking.service_id)
        .where(
            Booking.customer_id == customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(desc(Booking.scheduled_at))
        .limit(20)
    )
    history = bk_result.all()

    last_booking_date = None
    days_since_last_visit = None
    if history:
        last_bk = history[0][0]
        if last_bk.scheduled_at:
            last_booking_date = last_bk.scheduled_at
            if isinstance(last_booking_date, str):
                last_booking_date = datetime.fromisoformat(str(last_booking_date))
            if last_booking_date.tzinfo is None:
                last_booking_date = last_booking_date.replace(tzinfo=timezone.utc)
            days_since_last_visit = (datetime.now(timezone.utc) - last_booking_date).days

    # ── Service category frequency ──
    category_counts: dict[str, int] = {}
    service_history_ids = set()
    for bk, svc in history:
        cat = svc.category or "General"
        category_counts[cat] = category_counts.get(cat, 0) + 1
        service_history_ids.add(svc.id)
    top_category = max(category_counts, key=category_counts.get) if category_counts else None

    # ── Hair/skin condition ──
    damage = profile.hair_damage_level or 0
    skin_concerns = profile.primary_skin_concerns or []

    # ── Season-aware ──
    month = datetime.now().month
    season = "winter" if month in (11, 12, 1, 2) else "summer" if month in (3, 4, 5, 6) else "monsoon" if month in (7, 8, 9) else "autumn"

    # ── Climate data ──
    humidity = float(profile.local_humidity) if profile.local_humidity else None

    # ── Build recommendations ──
    candidates: list[dict] = []

    # Recommendation logic: overdue regular service
    if days_since_last_visit and days_since_last_visit > 30 and top_category:
        svc_result = await db.execute(
            select(Service)
            .where(Service.is_active == True, Service.category == top_category)
            .order_by(desc(Service.base_price))
            .limit(1)
        )
        svc = svc_result.scalar_one_or_none()
        if svc:
            urgency = "high" if days_since_last_visit > 60 else "medium"
            candidates.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": f"Your most-visited category '{top_category}' — last visit {days_since_last_visit} days ago",
                "urgency": urgency,
                "estimated_benefit": "Maintain regular care routine and prevent deterioration",
                "price": float(svc.base_price),
            })

    # Recommendation: hair treatment if damage is high
    if damage >= 5:
        svc_result = await db.execute(
            select(Service)
            .where(
                Service.is_active == True,
                func.lower(Service.category).in_(["hair treatment", "hair spa", "hair repair"]),
            )
            .order_by(Service.base_price)
            .limit(1)
        )
        svc = svc_result.scalar_one_or_none()
        if svc:
            candidates.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": f"Hair damage level is {damage}/10 — treatment needed to prevent further damage",
                "urgency": "high" if damage >= 7 else "medium",
                "estimated_benefit": "Reduce damage, improve texture and shine",
                "price": float(svc.base_price),
            })

    # Recommendation: skin treatment if concerns exist
    if skin_concerns:
        svc_result = await db.execute(
            select(Service)
            .where(
                Service.is_active == True,
                func.lower(Service.category).in_(["facial", "skin treatment", "cleanup"]),
            )
            .order_by(Service.base_price)
            .limit(1)
        )
        svc = svc_result.scalar_one_or_none()
        if svc:
            concern_str = ", ".join(skin_concerns[:2])
            candidates.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": f"Active skin concerns: {concern_str}",
                "urgency": "medium",
                "estimated_benefit": "Address skin concerns and improve complexion",
                "price": float(svc.base_price),
            })

    # Recommendation: seasonal service
    seasonal_categories = {
        "summer": ["de-tan", "facial", "hair spa"],
        "winter": ["hair spa", "moisturizing facial", "manicure"],
        "monsoon": ["anti-frizz treatment", "hair treatment", "pedicure"],
        "autumn": ["facial", "hair color", "cleanup"],
    }
    season_cats = seasonal_categories.get(season, [])
    if season_cats:
        svc_result = await db.execute(
            select(Service)
            .where(
                Service.is_active == True,
                func.lower(Service.category).in_([c.lower() for c in season_cats]),
            )
            .limit(1)
        )
        svc = svc_result.scalar_one_or_none()
        if svc:
            candidates.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": f"Seasonal recommendation for {season} — popular this time of year",
                "urgency": "low",
                "estimated_benefit": f"Seasonal care optimized for {season} conditions",
                "price": float(svc.base_price),
            })

    # Recommendation: humidity-based
    if humidity and humidity > 70:
        svc_result = await db.execute(
            select(Service)
            .where(
                Service.is_active == True,
                func.lower(Service.category).in_(["keratin", "smoothening", "anti-frizz treatment"]),
            )
            .limit(1)
        )
        svc = svc_result.scalar_one_or_none()
        if svc:
            candidates.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": f"Humidity is {humidity}% in {profile.city} — anti-frizz recommended",
                "urgency": "medium",
                "estimated_benefit": "Frizz control and smoother hair in humid conditions",
                "price": float(svc.base_price),
            })

    # Upcoming events
    if profile.upcoming_events:
        for event in profile.upcoming_events[:1]:
            svc_result = await db.execute(
                select(Service)
                .where(
                    Service.is_active == True,
                    func.lower(Service.category).in_(["bridal", "party makeup", "hair styling", "facial"]),
                )
                .limit(1)
            )
            svc = svc_result.scalar_one_or_none()
            if svc:
                candidates.append({
                    "service_id": svc.id,
                    "service_name": svc.name,
                    "category": svc.category,
                    "reason": f"Upcoming event: {event} — look your best",
                    "urgency": "high",
                    "estimated_benefit": "Event-ready look with professional styling",
                    "price": float(svc.base_price),
                })

    # Deduplicate by service_id, keep top 3
    seen_ids = set()
    top3 = []
    for c in candidates:
        if c["service_id"] not in seen_ids:
            seen_ids.add(c["service_id"])
            top3.append(c)
        if len(top3) >= 3:
            break

    # Persist recommendation snapshot
    profile.recommended_next_services = {"recommendations": top3}
    profile.recommendation_generated_at = datetime.now(timezone.utc)

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "days_since_last_visit": days_since_last_visit,
            "top_service_category": top_category,
            "season": season,
            "recommendations": top3,
        },
    )


next_best_service_agent = register_agent(AgentAction(
    name="next_best_service",
    description="Analyze customer history to recommend top 3 next-best services with urgency",
    track="personalization",
    feature="recommendation",
    method="post",
    path="/agents/track3/recommendation/next-best",
    handler=next_best_service_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.05"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 29. virtual_tryon_session  (PS-03.06)
# ─────────────────────────────────────────────────────────────────────────────

async def virtual_tryon_session_handler(
    customer_id: str = Query(...),
    tryon_type: str = Query(..., description="hairstyle, color, or makeup"),
    style_value: str = Query(..., description="Style or color to try on"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Create an AR mirror virtual try-on session and return session data."""
    await check_customer_ownership(user, customer_id, db)

    # Validate customer exists
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # Map tryon_type to MirrorSessionType
    type_map = {
        "hairstyle": MirrorSessionType.HAIRSTYLE,
        "color": MirrorSessionType.HAIR_COLOR,
        "makeup": MirrorSessionType.MAKEUP,
    }
    session_type = type_map.get(tryon_type.lower())
    if not session_type:
        raise HTTPException(status_code=400, detail=f"Invalid tryon_type '{tryon_type}'. Use: hairstyle, color, makeup")

    # Get digital twin data if available
    twin_result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == customer_id)
    )
    twin = twin_result.scalar_one_or_none()

    # Determine initiator
    initiator = MirrorInitiator.CUSTOMER if enum_val(user.role) == "customer" else MirrorInitiator.STYLIST

    # Get customer's preferred location
    location_id = profile.preferred_location_id

    # Build tryon data
    tryon_data = {
        "type": tryon_type,
        "value": style_value,
        "customer_hair_profile": {
            "hair_type": profile.hair_type,
            "hair_texture": profile.hair_texture,
            "current_color": profile.current_hair_color,
            "face_shape": None,  # Would come from digital twin
        },
        "twin_available": twin is not None and twin.is_active,
        "twin_model_url": twin.model_data_url if twin and twin.is_active else None,
    }

    # Create AR session record
    ar_session = ARMirrorSession(
        customer_id=customer_id,
        location_id=location_id,
        initiated_by=initiator,
        session_type=session_type,
        tryons={"selections": [{"type": tryon_type, "value": style_value, "timestamp": str(datetime.now(timezone.utc))}]},
    )
    db.add(ar_session)
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "session_id": ar_session.id,
            "customer_id": customer_id,
            "session_type": enum_val(session_type),
            "initiated_by": enum_val(initiator),
            "tryon_data": tryon_data,
            "message": f"Virtual try-on session started for {tryon_type}: {style_value}",
        },
    )


virtual_tryon_session_agent = register_agent(AgentAction(
    name="virtual_tryon_session",
    description="Create an AR mirror virtual try-on session for hairstyle, color, or makeup",
    track="personalization",
    feature="ar_mirror",
    method="post",
    path="/agents/track3/ar/virtual-tryon",
    handler=virtual_tryon_session_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.06"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 30. journey_plan_generate  (PS-03.07)
# ─────────────────────────────────────────────────────────────────────────────

async def journey_plan_generate_handler(
    customer_id: str = Query(...),
    goal: str = Query(..., description="Beauty goal, e.g. 'repair damaged hair', 'clear acne'"),
    duration_weeks: int = Query(12, ge=4, le=52, description="Plan duration in weeks"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Generate a milestone-based beauty journey plan for a customer."""
    await check_customer_ownership(user, customer_id, db)

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Determine goal-aligned service categories ──
    goal_lower = goal.lower()
    target_categories = []
    if any(w in goal_lower for w in ["hair", "damage", "repair", "fall", "growth"]):
        target_categories = ["hair treatment", "hair spa", "scalp treatment"]
    elif any(w in goal_lower for w in ["color", "colour", "blonde", "highlights"]):
        target_categories = ["hair color", "highlights", "hair treatment"]
    elif any(w in goal_lower for w in ["skin", "acne", "glow", "pigment", "complexion"]):
        target_categories = ["facial", "skin treatment", "cleanup"]
    elif any(w in goal_lower for w in ["bridal", "wedding"]):
        target_categories = ["bridal", "facial", "hair styling", "makeup", "manicure", "pedicure"]
    elif any(w in goal_lower for w in ["relax", "wellness", "stress"]):
        target_categories = ["hair spa", "facial", "head massage"]
    else:
        target_categories = ["hair treatment", "facial", "hair spa"]

    # ── Fetch relevant services ──
    svc_result = await db.execute(
        select(Service)
        .where(
            Service.is_active == True,
            func.lower(Service.category).in_([c.lower() for c in target_categories]),
        )
        .order_by(Service.base_price)
    )
    services = svc_result.scalars().all()

    if not services:
        # Fallback to any active services
        svc_result = await db.execute(
            select(Service).where(Service.is_active == True).limit(5)
        )
        services = svc_result.scalars().all()

    # ── Build milestones ──
    milestones = []
    total_estimated_cost = 0.0
    visit_interval = max(2, duration_weeks // min(len(services) + 2, duration_weeks // 2))

    week = 1
    svc_idx = 0
    while week <= duration_weeks and services:
        svc = services[svc_idx % len(services)]
        svc_cost = float(svc.base_price)

        # Home care tasks vary by week
        home_care_tasks = []
        if week == 1:
            home_care_tasks = [
                "Begin daily routine: gentle cleansing + moisturizing",
                "Start photo-documenting for progress tracking",
            ]
        elif week <= duration_weeks // 3:
            home_care_tasks = [
                "Continue prescribed daily routine",
                f"Weekly deep conditioning or mask (for {goal})",
                "Monitor and note any improvements",
            ]
        elif week <= 2 * duration_weeks // 3:
            home_care_tasks = [
                "Maintain consistent routine — results building",
                "Adjust products if needed based on progress",
            ]
        else:
            home_care_tasks = [
                "Maintenance phase — continue what works",
                "Prepare for transition to long-term routine",
            ]

        expected_outcome = f"Week {week}: "
        pct = int((week / duration_weeks) * 100)
        if pct <= 25:
            expected_outcome += "Initial assessment and treatment foundation"
        elif pct <= 50:
            expected_outcome += "Visible early improvements in target area"
        elif pct <= 75:
            expected_outcome += "Significant progress toward goal"
        else:
            expected_outcome += "Near-goal results with maintenance focus"

        milestones.append({
            "week": week,
            "salon_visit": {
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "cost": svc_cost,
                "duration_minutes": svc.duration_minutes,
            },
            "home_care_tasks": home_care_tasks,
            "expected_outcome": expected_outcome,
        })
        total_estimated_cost += svc_cost
        svc_idx += 1
        week += visit_interval

    # ── Persist the plan ──
    plan = BeautyJourneyPlan(
        customer_id=customer_id,
        plan_duration_weeks=duration_weeks,
        primary_goal=goal,
        generated_at=datetime.now(timezone.utc),
        milestones={"milestones": milestones},
        expected_outcomes={
            "goal": goal,
            "expected_timeline_weeks": duration_weeks,
            "total_visits": len(milestones),
        },
        estimated_total_cost=total_estimated_cost,
    )
    db.add(plan)
    await db.flush()

    # Update customer profile
    profile.primary_goal = goal
    profile.goal_timeline_weeks = duration_weeks
    profile.goal_progress_pct = 0

    return APIResponse(
        success=True,
        data={
            "plan_id": plan.id,
            "customer_id": customer_id,
            "goal": goal,
            "duration_weeks": duration_weeks,
            "total_visits": len(milestones),
            "total_estimated_cost": round(total_estimated_cost, 2),
            "milestones": milestones,
        },
    )


journey_plan_generate_agent = register_agent(AgentAction(
    name="journey_plan_generate",
    description="Generate a milestone-based beauty journey plan with salon visits, home care, and cost estimates",
    track="personalization",
    feature="journey",
    method="post",
    path="/agents/track3/journey/generate",
    handler=journey_plan_generate_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.07"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 31. climate_adjust_service  (PS-03.08)
# ─────────────────────────────────────────────────────────────────────────────

async def climate_adjust_service_handler(
    customer_id: str = Query(...),
    service_id: str = Query(...),
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Get climate-based adjustments for a service at a specific location."""

    # ── Fetch location ──
    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # ── Fetch service ──
    svc_result = await db.execute(select(Service).where(Service.id == service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # ── Fetch customer ──
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── Get climate data for location's city ──
    today = date.today()
    clm_result = await db.execute(
        select(ClimateRecommendation)
        .where(ClimateRecommendation.city == location.city)
        .order_by(desc(ClimateRecommendation.date_for))
        .limit(1)
    )
    climate = clm_result.scalar_one_or_none()

    temp = float(climate.temperature_celsius) if climate and climate.temperature_celsius else None
    humidity = float(climate.humidity_pct) if climate and climate.humidity_pct else None
    uv = float(climate.uv_index) if climate and climate.uv_index else None
    aqi = float(climate.aqi) if climate and climate.aqi else None

    # ── Product substitutions ──
    product_substitutions = []
    if humidity and humidity > 75:
        product_substitutions.append({
            "original": "Standard conditioner",
            "substitute": "Lightweight anti-humidity conditioner",
            "reason": f"Humidity is {humidity}% — heavy products will weigh hair down",
        })
        product_substitutions.append({
            "original": "Regular styling cream",
            "substitute": "Anti-frizz serum",
            "reason": "Frizz prevention in high humidity",
        })
    elif humidity and humidity < 30:
        product_substitutions.append({
            "original": "Regular conditioner",
            "substitute": "Deep moisturizing conditioner",
            "reason": f"Low humidity ({humidity}%) — extra hydration needed",
        })

    if temp and temp > 35:
        product_substitutions.append({
            "original": "Heavy hair oil",
            "substitute": "Lightweight hair serum",
            "reason": f"High temperature ({temp}C) — lighter products recommended",
        })
    elif temp and temp < 15:
        product_substitutions.append({
            "original": "Lightweight moisturizer",
            "substitute": "Rich protective cream",
            "reason": f"Cold weather ({temp}C) — extra moisture barrier needed",
        })

    if uv and uv > 6:
        product_substitutions.append({
            "original": "Standard finishing spray",
            "substitute": "UV-protection finishing spray",
            "reason": f"UV index is {uv} — UV protection critical",
        })

    if aqi and aqi > 150:
        product_substitutions.append({
            "original": "Regular face wash",
            "substitute": "Anti-pollution face cleanser",
            "reason": f"AQI is {aqi} — pollution protection needed",
        })

    # ── Technique modifications ──
    technique_modifications = []
    if humidity and humidity > 75:
        technique_modifications.append("Use cold-air setting for blow-drying to seal cuticles")
        technique_modifications.append("Apply anti-frizz treatment before styling")
    if temp and temp > 35:
        technique_modifications.append("Reduce processing time for chemical services by 10-15%")
        technique_modifications.append("Use cool water for final rinse")
    if temp and temp < 15:
        technique_modifications.append("Warm products before application for better absorption")
        technique_modifications.append("Extend massage time to improve circulation in cold weather")

    # ── Processing time adjustment ──
    processing_time_adj = 0
    if service.is_chemical:
        if temp and temp > 35:
            processing_time_adj = -5  # Heat accelerates processing
        elif temp and temp < 15:
            processing_time_adj = 5  # Cold slows processing
        if humidity and humidity > 80:
            processing_time_adj -= 3  # High humidity helps absorption

    # ── Home care climate tips ──
    home_care_tips = []
    if humidity and humidity > 70:
        home_care_tips.append("Use anti-humidity hair spray daily")
        home_care_tips.append("Wash hair with lukewarm water, not hot")
    if temp and temp > 35:
        home_care_tips.append("Rinse hair with cool water after outdoor exposure")
        home_care_tips.append("Apply SPF-infused leave-in conditioner before going out")
    if uv and uv > 6:
        home_care_tips.append("Wear a hat or scarf when outdoors between 10 AM and 4 PM")
        home_care_tips.append("Reapply sunscreen every 2 hours on exposed skin")
    if aqi and aqi > 100:
        home_care_tips.append("Wash hair every evening to remove pollutant buildup")
        home_care_tips.append("Use antioxidant-rich skincare products")
    if temp and temp < 15:
        home_care_tips.append("Use a humidifier indoors to prevent skin dryness")
        home_care_tips.append("Apply overnight hair oil treatments weekly")

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "service_id": service_id,
            "service_name": service.name,
            "location": {"id": location.id, "name": location.name, "city": location.city},
            "climate": {
                "temperature_celsius": temp,
                "humidity_pct": humidity,
                "uv_index": uv,
                "aqi": aqi,
                "weather": climate.weather_condition if climate else None,
                "date": str(climate.date_for) if climate else None,
            },
            "product_substitutions": product_substitutions,
            "technique_modifications": technique_modifications,
            "processing_time_adjustment_mins": processing_time_adj,
            "home_care_climate_tips": home_care_tips,
        },
    )


climate_adjust_service_agent = register_agent(AgentAction(
    name="climate_adjust_service",
    description="Get climate-based product substitutions, technique modifications, and processing time adjustments",
    track="personalization",
    feature="climate",
    method="post",
    path="/agents/track3/climate/adjust-service",
    handler=climate_adjust_service_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-03.08"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 32. personalized_loyalty_offer  (PS-03.09)
# ─────────────────────────────────────────────────────────────────────────────

async def personalized_loyalty_offer_handler(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Compute LTV tier and generate a personalized loyalty offer."""
    await check_customer_ownership(user, customer_id, db)

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # ── LTV tier calculation ──
    ltv = float(profile.lifetime_value) if profile.lifetime_value else 0
    if ltv >= 50000:
        tier = "platinum"
    elif ltv >= 25000:
        tier = "gold"
    elif ltv >= 10000:
        tier = "silver"
    else:
        tier = "bronze"

    # ── Most booked service category ──
    cat_result = await db.execute(
        select(Service.category, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.customer_id == customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .group_by(Service.category)
        .order_by(desc(func.count(Booking.id)))
        .limit(1)
    )
    top_cat_row = cat_result.first()
    most_booked_category = top_cat_row[0] if top_cat_row else None

    # ── Days since last visit ──
    last_bk_result = await db.execute(
        select(Booking.scheduled_at)
        .where(
            Booking.customer_id == customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(desc(Booking.scheduled_at))
        .limit(1)
    )
    last_bk_row = last_bk_result.first()
    days_since = None
    if last_bk_row and last_bk_row[0]:
        last_dt = last_bk_row[0]
        if isinstance(last_dt, str):
            last_dt = datetime.fromisoformat(str(last_dt))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        days_since = (datetime.now(timezone.utc) - last_dt).days

    # ── Loyalty program data ──
    lp_result = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.customer_id == customer_id)
    )
    loyalty = lp_result.scalar_one_or_none()

    # ── Generate offer ──
    archetype = profile.dominant_archetype
    beauty_score = profile.beauty_score or 50

    # Offer logic based on tier, recency, category
    offer_type = "discount"
    discount_pct = 10
    message = ""
    offer_details = {}

    if tier == "platinum":
        discount_pct = 20
        offer_type = "vip_experience"
        message = f"As our Platinum guest, enjoy a complimentary upgrade on your next {most_booked_category or 'service'} visit"
        offer_details = {
            "upgrade_service": most_booked_category,
            "complimentary_addon": "Head massage + Aromatherapy",
            "discount_percent": discount_pct,
        }
    elif tier == "gold":
        discount_pct = 15
        offer_type = "bundle_discount"
        message = f"Gold member special: {discount_pct}% off on your favorite {most_booked_category or 'services'}"
        offer_details = {
            "bundle_category": most_booked_category,
            "discount_percent": discount_pct,
            "bonus_points": 200,
        }
    elif tier == "silver":
        discount_pct = 10
        offer_type = "comeback_offer" if days_since and days_since > 45 else "category_discount"
        if days_since and days_since > 45:
            message = f"We miss you! Come back and get {discount_pct}% off + bonus loyalty points"
            offer_details = {"discount_percent": discount_pct, "bonus_points": 150}
        else:
            message = f"Silver member deal: {discount_pct}% off {most_booked_category or 'your next visit'}"
            offer_details = {"discount_percent": discount_pct, "category": most_booked_category}
    else:
        discount_pct = 5
        offer_type = "trial_upgrade"
        message = "Try a premium service at a special introductory rate!"
        offer_details = {"discount_percent": discount_pct, "trial_service": "Premium Hair Spa"}

    # Archetype-based personalization
    if archetype:
        archetype_messages = {
            "fire": "Bold and beautiful — your fiery spirit deserves a treat!",
            "earth": "Grounded and radiant — nurture yourself with this special offer.",
            "water": "Flow into beauty — a calming experience awaits you.",
            "air": "Light and free — refresh your look with this exclusive deal.",
            "ether": "Transcend the ordinary — elevate your beauty ritual.",
        }
        archetype_msg = archetype_messages.get(archetype.lower())
        if archetype_msg:
            message = f"{archetype_msg} {message}"

    # Beauty score progress bonus
    if beauty_score >= 80:
        offer_details["beauty_score_bonus"] = "Extra 5% off for maintaining an excellent beauty score"
        discount_pct += 5

    valid_until = datetime.now(timezone.utc) + timedelta(days=30)

    # ── Persist the offer ──
    offer = PersonalizedOffer(
        customer_id=customer_id,
        offer_type=offer_type,
        title=f"{tier.capitalize()} {offer_type.replace('_', ' ').title()}",
        description=message,
        discount_percent=discount_pct,
        valid_from=datetime.now(timezone.utc),
        valid_until=valid_until,
        service_ids=[],
        ai_reason=f"LTV tier: {tier}, most booked: {most_booked_category}, days since last: {days_since}, archetype: {archetype}",
    )
    db.add(offer)
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "tier": tier,
            "lifetime_value": ltv,
            "loyalty_points": loyalty.total_points if loyalty else 0,
            "redeemable_points": loyalty.redeemable_points if loyalty else 0,
            "most_booked_category": most_booked_category,
            "days_since_last_visit": days_since,
            "beauty_score": beauty_score,
            "archetype": archetype,
            "offer_id": offer.id,
            "offer_type": offer_type,
            "offer_details": offer_details,
            "message": message,
            "valid_until": str(valid_until.date()),
        },
    )


personalized_loyalty_offer_agent = register_agent(AgentAction(
    name="personalized_loyalty_offer",
    description="Compute LTV tier and generate a personalized loyalty offer based on history and archetype",
    track="personalization",
    feature="loyalty",
    method="post",
    path="/agents/track3/loyalty/personalized-offer",
    handler=personalized_loyalty_offer_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.09"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 33. occasion_planner  (PS-03.10)
# ─────────────────────────────────────────────────────────────────────────────

async def occasion_planner_handler(
    customer_id: str = Query(...),
    occasion_type: str = Query(..., description="wedding, birthday, festival, party"),
    occasion_date: str = Query(..., description="YYYY-MM-DD"),
    budget: Optional[float] = Query(None, description="Max budget in currency units"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "customer", "super_admin"])),
):
    """Generate a multi-visit preparation plan leading up to an occasion."""
    await check_customer_ownership(user, customer_id, db)

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    profile = cp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    try:
        occ_date = date.fromisoformat(occasion_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid occasion_date format. Use YYYY-MM-DD")

    days_until = (occ_date - date.today()).days
    if days_until < 0:
        raise HTTPException(status_code=400, detail="Occasion date is in the past")

    # ── Map occasion to service categories ──
    occasion_categories: dict[str, list[str]] = {
        "wedding": ["bridal", "facial", "hair styling", "makeup", "manicure", "pedicure", "hair spa", "waxing", "threading"],
        "birthday": ["facial", "hair styling", "makeup", "manicure", "pedicure"],
        "festival": ["facial", "hair styling", "threading", "waxing", "mehendi", "makeup"],
        "party": ["hair styling", "makeup", "manicure", "facial"],
    }
    categories = occasion_categories.get(occasion_type.lower(), ["facial", "hair styling", "makeup"])

    # ── Fetch services ──
    svc_result = await db.execute(
        select(Service)
        .where(
            Service.is_active == True,
            func.lower(Service.category).in_([c.lower() for c in categories]),
        )
        .order_by(Service.base_price)
    )
    services = svc_result.scalars().all()

    if not services:
        svc_result = await db.execute(
            select(Service).where(Service.is_active == True).limit(6)
        )
        services = svc_result.scalars().all()

    # ── Build visit plan ──
    visits = []
    total_cost = 0.0

    # Pre-occasion preparation tiers
    if days_until >= 60:
        # 3+ visits: deep prep, mid prep, final
        visit_dates = [
            occ_date - timedelta(days=max(days_until - 7, 45)),
            occ_date - timedelta(days=14),
            occ_date - timedelta(days=1),
        ]
    elif days_until >= 30:
        visit_dates = [
            occ_date - timedelta(days=21),
            occ_date - timedelta(days=7),
            occ_date - timedelta(days=1),
        ]
    elif days_until >= 14:
        visit_dates = [
            occ_date - timedelta(days=10),
            occ_date - timedelta(days=1),
        ]
    elif days_until >= 3:
        visit_dates = [
            occ_date - timedelta(days=2),
            occ_date,
        ]
    else:
        visit_dates = [occ_date]

    # Assign services per visit
    prep_notes_map = {
        0: "Deep preparation: treatments and base care",
        1: "Mid-stage: touch-ups and fine-tuning",
        2: "Final visit: event-day look and polish",
    }

    svc_idx = 0
    for i, vd in enumerate(visit_dates):
        visit_services = []
        # Assign 2-3 services per visit
        n_services = min(3, len(services) - svc_idx) if svc_idx < len(services) else 1
        if n_services <= 0:
            svc_idx = 0
            n_services = min(2, len(services))

        visit_cost = 0.0
        for _ in range(n_services):
            svc = services[svc_idx % len(services)]
            svc_cost = float(svc.base_price)
            visit_services.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "price": svc_cost,
                "duration_minutes": svc.duration_minutes,
            })
            visit_cost += svc_cost
            svc_idx += 1

        # If budget given, check if we're over
        if budget and (total_cost + visit_cost) > budget:
            # Trim services to fit
            while visit_services and (total_cost + visit_cost) > budget:
                removed = visit_services.pop()
                visit_cost -= removed["price"]
            if not visit_services:
                break

        total_cost += visit_cost

        prep_note = prep_notes_map.get(i, "Maintenance and care visit")
        if i == len(visit_dates) - 1:
            prep_note = f"Final preparation for {occasion_type}: styling, makeup, finishing touches"

        visits.append({
            "visit_date": str(vd),
            "days_before_occasion": (occ_date - vd).days,
            "services": visit_services,
            "preparation_notes": prep_note,
            "estimated_cost": round(visit_cost, 2),
        })

    # ── Save to customer profile ──
    plan_data = {
        "occasion_type": occasion_type,
        "occasion_date": occasion_date,
        "visits": visits,
        "total_cost": round(total_cost, 2),
        "budget": budget,
        "generated_at": str(datetime.now(timezone.utc)),
    }
    existing_plans = profile.occasion_plans or {}
    if not isinstance(existing_plans, dict):
        existing_plans = {}
    existing_plans[occasion_date] = plan_data
    profile.occasion_plans = existing_plans

    budget_status = None
    if budget:
        if total_cost <= budget:
            budget_status = f"Within budget ({round(total_cost, 2)} of {budget})"
        else:
            budget_status = f"Over budget ({round(total_cost, 2)} vs {budget} limit)"

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "occasion_type": occasion_type,
            "occasion_date": occasion_date,
            "days_until_occasion": days_until,
            "total_visits": len(visits),
            "total_estimated_cost": round(total_cost, 2),
            "budget": budget,
            "budget_status": budget_status,
            "visits": visits,
        },
    )


occasion_planner_agent = register_agent(AgentAction(
    name="occasion_planner",
    description="Generate a multi-visit occasion preparation plan (wedding/birthday/festival/party) with budget control",
    track="personalization",
    feature="occasion",
    method="post",
    path="/agents/track3/occasion/plan",
    handler=occasion_planner_handler,
    roles=["stylist", "salon_manager", "customer"],
    ps_codes=["PS-03.10"],
))
