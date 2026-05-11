"""Skin Tone AI Bot router — Feature 2.

Hybrid approach: server-side Gemini Vision analysis (primary) +
browser MediaPipe live preview (client-side, no upload needed).
Results auto-saved to the customer's Beauty Passport.
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import CustomerProfile
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.skintone_service import analyze_skin_tone

router = APIRouter(prefix="/skin-tone", tags=["Skin Tone AI Bot"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10


@router.post("/analyze", response_model=APIResponse)
async def analyze(
    file: UploadFile = File(...),
    save_to_passport: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a selfie → server analyses skin tone, undertone, face shape, and returns
    personalized beauty recommendations. Result optionally saved to Beauty Passport.

    Frontend sends image from:
    - Camera capture (after MediaPipe browser preview)
    - File upload (photo library)
    """
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}. Use JPEG, PNG, or WebP.")

    image_data = await file.read()
    if len(image_data) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, f"Image too large. Max {MAX_SIZE_MB}MB.")

    analysis = await analyze_skin_tone(image_data, file.content_type)

    # Auto-save to Beauty Passport if requested and user is a customer
    if save_to_passport:
        passport_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        passport = passport_result.scalar_one_or_none()
        if passport:
            passport.skin_tone = analysis.get("skin_tone")
            passport.undertone = analysis.get("undertone")
            passport.skin_type = analysis.get("skin_type")
            # Store full analysis in a JSON field
            existing_meta = passport.recommended_next_services or {}
            existing_meta["skin_tone_analysis"] = analysis
            passport.recommended_next_services = existing_meta
            await db.commit()

    return APIResponse(
        success=True,
        message="Skin tone analysis complete",
        data={
            "analysis": analysis,
            "saved_to_passport": save_to_passport and passport is not None if save_to_passport else False,
        },
    )


@router.get("/my-analysis", response_model=APIResponse)
async def get_my_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the saved skin tone analysis from the customer's Beauty Passport."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    passport = result.scalar_one_or_none()
    if not passport:
        raise HTTPException(404, "Beauty Passport not found. Complete your profile first.")

    skin_meta = (passport.recommended_next_services or {}).get("skin_tone_analysis")
    return APIResponse(
        success=True,
        message="Skin tone analysis retrieved",
        data={
            "skin_tone": passport.skin_tone,
            "undertone": passport.undertone,
            "skin_type": passport.skin_type,
            "full_analysis": skin_meta,
            "has_analysis": skin_meta is not None,
        },
    )


@router.get("/recommendations/{skin_tone}", response_model=APIResponse)
async def get_recommendations_by_tone(skin_tone: str):
    """Public endpoint — get beauty recommendations for a given skin tone.
    Useful for staff to quickly look up recommendations without login.
    skin_tone: Fair | Medium | Dusky | Deep
    """
    RECOMMENDATIONS = {
        "fair": {
            "hair_colors": ["Platinum Blonde", "Golden Blonde", "Light Auburn", "Strawberry Blonde"],
            "avoid_hair": ["Jet Black (can look harsh)", "Very Dark Brown"],
            "lip_shades": ["Soft Pink", "Peach", "Coral", "Light Berry"],
            "skincare": ["Brightening Facial", "Vitamin C Treatment", "Gentle Hydra Facial"],
            "tip": "Use SPF 50+ daily. Fair skin is more prone to sunburn and pigmentation.",
        },
        "medium": {
            "hair_colors": ["Copper Brown", "Mahogany", "Chestnut", "Warm Brunette"],
            "avoid_hair": ["Platinum Blonde", "Ash Grey"],
            "lip_shades": ["Berry", "Terracotta", "Nude Pink", "Deep Rose"],
            "skincare": ["Vitamin C Facial", "Hydra Facial", "Glow Treatment"],
            "tip": "Warm-toned products enhance your natural radiance. Avoid cool-toned foundations.",
        },
        "dusky": {
            "hair_colors": ["Rich Burgundy", "Dark Chocolate", "Espresso", "Deep Auburn"],
            "avoid_hair": ["Bleached colours (require multiple sessions, can damage)"],
            "lip_shades": ["Plum", "Deep Berry", "Brick Red", "Chocolate Brown"],
            "skincare": ["Brightening Facial", "De-Tan Treatment", "Even-Tone Mask"],
            "tip": "Bold, deep shades complement your skin tone beautifully. Own them.",
        },
        "deep": {
            "hair_colors": ["Deep Burgundy", "Dark Cherry", "Blue-Black", "Rich Espresso"],
            "avoid_hair": ["Very light colours without proper toning"],
            "lip_shades": ["Berry", "Plum", "Deep Red", "Warm Bronze"],
            "skincare": ["Brightening Treatment", "Kojic Acid Facial", "Moisture Boost"],
            "tip": "Gold and copper jewel tones are your power shades. Your melanin-rich skin ages beautifully.",
        },
    }

    key = skin_tone.lower()
    recs = RECOMMENDATIONS.get(key)
    if not recs:
        raise HTTPException(400, f"Unknown skin tone '{skin_tone}'. Valid: Fair, Medium, Dusky, Deep")

    return APIResponse(
        success=True,
        message=f"Recommendations for {skin_tone.title()} skin tone",
        data={"skin_tone": skin_tone.title(), **recs},
    )
