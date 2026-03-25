"""AR Mirror router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db, enum_val
from app.dependencies import get_current_user
from app.models import ARMirrorSession
from app.schemas.common import APIResponse
from app.schemas.entities import MirrorSessionUpdate

router = APIRouter(prefix="/mirror", tags=["AR Mirror"])

# ── Static style catalogue served to the AR Mirror page ──

_HAIRSTYLES = [
    {"name": "Bob with Curtain Bangs", "category": "Short", "trending": True,
     "img": "/images/mirror/bob.png"},
    {"name": "Layered Waves", "category": "Medium", "trending": True,
     "img": "/images/mirror/waves.png"},
    {"name": "Sleek Straight", "category": "Long", "trending": False,
     "img": "/images/mirror/straight.png"},
    {"name": "Pixie Cut", "category": "Short", "trending": True,
     "img": "/images/mirror/pixie.png"},
    {"name": "French Bob", "category": "Short", "trending": False,
     "img": "/images/mirror/french_bob.png"},
    {"name": "Soft Layers", "category": "Medium", "trending": False,
     "img": "/images/mirror/soft_layers.png"},
    {"name": "Blunt Cut", "category": "Long", "trending": False,
     "img": "/images/mirror/blunt.png"},
    {"name": "Shag Cut", "category": "Medium", "trending": True,
     "img": "/images/mirror/waves.png"}, 
    {"name": "Warm Copper Balayage", "category": "Color", "trending": True,
     "img": "/images/mirror/copper.png"},
    {"name": "Ash Blonde", "category": "Color", "trending": True,
     "img": "/images/mirror/ash_blonde.png"},
    {"name": "Honey Highlights", "category": "Color", "trending": False,
     "img": "/images/mirror/honey.png"},
    {"name": "Rich Burgundy", "category": "Color", "trending": False,
     "img": "/images/mirror/burgundy.png"},
    {"name": "Caramel Ombré", "category": "Color", "trending": True,
     "img": "/images/mirror/ombre.png"},
    {"name": "Platinum Blonde", "category": "Color", "trending": False,
     "img": "/images/mirror/ash_blonde.png"}, # Use Ash Blonde as fallback
]

_MAKEUP_LOOKS = [
    {"name": "Natural Glow", "desc": "Dewy skin, soft blush, nude lip",
     "icon": "/images/mirror/makeup_natural.png"},
    {"name": "Bridal Glam", "desc": "Full coverage, shimmer eyes, bold lip",
     "icon": "/images/mirror/makeup_bridal.png"},
    {"name": "Smokey Eye", "desc": "Dark blended shadow, winged liner",
     "icon": "/images/mirror/smokey_eye.png"},
    {"name": "Soft Glam", "desc": "Warm tones, bronzed skin, glossy lip",
     "icon": "/images/mirror/makeup_soft_glam.png"},
    {"name": "Bold Red Lip", "desc": "Classic red lip with minimal eye",
     "icon": "/images/mirror/makeup_bridal.png"}, # Local high-quality glam face
    {"name": "Korean Glass Skin", "desc": "Dewy, translucent, barely-there makeup",
     "icon": "/images/mirror/makeup_natural.png"}, # Local high-quality dewy face
    {"name": "Festival Look", "desc": "Glitter, bold colors, creative liner",
     "icon": "/images/mirror/smokey_eye.png"}, # Local high-quality dramatic face
    {"name": "Everyday Office", "desc": "Polished, neutral, professional",
     "icon": "/images/mirror/makeup_natural.png"}, # Local high-quality professional face
]

@router.get("/styles", response_model=APIResponse)
async def get_styles(user=Depends(get_current_user)):
    """Return the catalogue of hairstyles, hair colours and makeup looks."""
    return APIResponse(success=True, data={
        "hairstyles": _HAIRSTYLES,
        "makeup_looks": _MAKEUP_LOOKS,
    })


@router.get("/", response_model=APIResponse)
async def list_sessions(customer_id: UUID = None, location_id: UUID = None,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(ARMirrorSession).order_by(ARMirrorSession.created_at.desc()).limit(20)
    if customer_id:
        q = q.where(ARMirrorSession.customer_id == customer_id)
    # If customer is logged in, default to their sessions
    if not customer_id and not location_id and enum_val(user.role) == "customer":
        from app.models.customer import CustomerProfile
        cp_res = await db.execute(select(CustomerProfile).where(CustomerProfile.user_id == user.id))
        cp = cp_res.scalar_one_or_none()
        if cp:
            q = q.where(ARMirrorSession.customer_id == cp.id)
            
    if location_id:
        q = q.where(ARMirrorSession.location_id == location_id)
    result = await db.execute(q)
    sessions = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(s.id), "session_type": enum_val(s.session_type) if s.session_type else None,
        "saved_images": s.saved_images or [],
        "created_at": s.created_at.isoformat() if s.created_at else None,
    } for s in sessions])


@router.get("/{session_id}", response_model=APIResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(ARMirrorSession).where(ARMirrorSession.id == str(session_id)))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return APIResponse(success=True, data={
        "id": str(session.id), "session_type": enum_val(session.session_type),
        "saved_images": session.saved_images or [],
        "tryons": session.tryons or {},
    })


@router.post("/", response_model=APIResponse)
async def create_session(
    customer_id: UUID, location_id: UUID, session_type: str = "hairstyle",
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    session = ARMirrorSession(
        customer_id=str(customer_id), location_id=str(location_id),
        session_type=session_type
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return APIResponse(success=True, data={"id": str(session.id)}, message="Mirror session created")


@router.patch("/{session_id}", response_model=APIResponse)
async def update_session(
    session_id: UUID, update: MirrorSessionUpdate,
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    result = await db.execute(select(ARMirrorSession).where(ARMirrorSession.id == str(session_id)))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if update.session_type:
        session.session_type = update.session_type
    if update.saved_images is not None:
        session.saved_images = update.saved_images
    if update.tryons is not None:
        session.tryons = update.tryons
    if update.final_selection is not None:
        session.final_selection = update.final_selection
        
    await db.commit()
    await db.refresh(session)
    return APIResponse(success=True, message="Session updated")
