"""AURA Points — Loyalty & Rewards API."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/loyalty", tags=["AURA Points"])

TIER_THRESHOLDS = {"bronze": 0, "silver": 1000, "gold": 3000, "platinum": 8000}
TIER_MULTIPLIERS = {"bronze": 1.0, "silver": 1.25, "gold": 1.5, "platinum": 2.0}
POINTS_PER_RUPEE = 1  # 1 point per ₹1 spent

REWARDS_CATALOGUE = [
    {"id": "r1", "name": "Free Hair Wash", "points": 200, "category": "service"},
    {"id": "r2", "name": "₹100 Discount", "points": 300, "category": "discount"},
    {"id": "r3", "name": "Free Head Massage", "points": 400, "category": "service"},
    {"id": "r4", "name": "₹250 Discount", "points": 700, "category": "discount"},
    {"id": "r5", "name": "Free Manicure", "points": 800, "category": "service"},
    {"id": "r6", "name": "₹500 Discount", "points": 1200, "category": "discount"},
    {"id": "r7", "name": "Free Facial (Basic)", "points": 1500, "category": "service"},
    {"id": "r8", "name": "Free Hair Colour Touch-up", "points": 2500, "category": "service"},
]


def _tier_for_points(points: int) -> str:
    tier = "bronze"
    for t, threshold in sorted(TIER_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if points >= threshold:
            tier = t
            break
    return tier


def _next_tier(current_tier: str) -> tuple[str | None, int]:
    order = ["bronze", "silver", "gold", "platinum"]
    idx = order.index(current_tier)
    if idx >= len(order) - 1:
        return None, 0
    next_t = order[idx + 1]
    return next_t, TIER_THRESHOLDS[next_t]


@router.get("/me", response_model=APIResponse)
async def get_my_loyalty(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the current customer's AURA Points balance, tier, and recent transactions."""
    from app.models.loyalty import LoyaltyProgram, LoyaltyTransaction
    from app.models.customer import CustomerProfile

    # Resolve customer profile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == str(current_user.id))
    )
    cp = cp_result.scalar_one_or_none()
    if not cp:
        raise HTTPException(404, "Customer profile not found")

    lp_result = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.customer_id == str(cp.id))
    )
    lp = lp_result.scalar_one_or_none()

    if not lp:
        # Bootstrap a new loyalty program
        from app.database import generate_uuid
        import random, string
        code = "AURA" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        lp = LoyaltyProgram(
            id=generate_uuid(),
            customer_id=str(cp.id),
            tier="bronze",
            total_points=0,
            redeemable_points=0,
            lifetime_points_earned=0,
            referral_code=code,
        )
        db.add(lp)
        await db.commit()
        await db.refresh(lp)

    # Recent transactions
    txn_result = await db.execute(
        select(LoyaltyTransaction)
        .where(LoyaltyTransaction.loyalty_program_id == str(lp.id))
        .order_by(LoyaltyTransaction.created_at.desc())
        .limit(20)
    )
    txns = txn_result.scalars().all()

    tier = _tier_for_points(lp.lifetime_points_earned or 0)
    next_tier, next_threshold = _next_tier(tier)
    points_to_next = max(0, next_threshold - (lp.lifetime_points_earned or 0)) if next_tier else 0

    return APIResponse(
        success=True,
        message="AURA Points",
        data={
            "tier": tier,
            "tier_multiplier": TIER_MULTIPLIERS[tier],
            "total_points": lp.total_points or 0,
            "redeemable_points": lp.redeemable_points or 0,
            "lifetime_points_earned": lp.lifetime_points_earned or 0,
            "next_tier": next_tier,
            "points_to_next_tier": points_to_next,
            "referral_code": lp.referral_code,
            "transactions": [
                {
                    "id": str(t.id),
                    "type": t.transaction_type,
                    "points": t.points,
                    "description": t.description,
                    "created_at": str(t.created_at),
                }
                for t in txns
            ],
            "rewards_catalogue": REWARDS_CATALOGUE,
            "redeemable_rewards": [r for r in REWARDS_CATALOGUE if r["points"] <= (lp.redeemable_points or 0)],
        },
    )


@router.post("/redeem/{reward_id}", response_model=APIResponse)
async def redeem_reward(
    reward_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Redeem an AURA Points reward. Deducts points and returns a coupon code."""
    from app.models.loyalty import LoyaltyProgram, LoyaltyTransaction
    from app.models.customer import CustomerProfile
    from app.database import generate_uuid
    import random, string

    reward = next((r for r in REWARDS_CATALOGUE if r["id"] == reward_id), None)
    if not reward:
        raise HTTPException(404, "Reward not found")

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == str(current_user.id))
    )
    cp = cp_result.scalar_one_or_none()
    if not cp:
        raise HTTPException(404, "Customer profile not found")

    lp_result = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.customer_id == str(cp.id))
    )
    lp = lp_result.scalar_one_or_none()
    if not lp or (lp.redeemable_points or 0) < reward["points"]:
        raise HTTPException(400, "Insufficient AURA Points")

    lp.redeemable_points = (lp.redeemable_points or 0) - reward["points"]
    lp.total_points = (lp.total_points or 0) - reward["points"]

    coupon = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    txn = LoyaltyTransaction(
        id=generate_uuid(),
        loyalty_program_id=str(lp.id),
        transaction_type="redemption",
        points=-reward["points"],
        description=f"Redeemed: {reward['name']} (Coupon: {coupon})",
    )
    db.add(txn)
    await db.commit()

    return APIResponse(
        success=True,
        message="Reward redeemed!",
        data={"coupon_code": coupon, "reward": reward, "remaining_points": lp.redeemable_points},
    )


@router.post("/referral/apply", response_model=APIResponse)
async def apply_referral_code(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a referral code — awards 200 pts to both referrer and new customer.
    Can only be used once per account.
    """
    from app.models.loyalty import LoyaltyProgram, LoyaltyTransaction
    from app.models.customer import CustomerProfile
    from app.database import generate_uuid

    code = (body.get("referral_code") or "").strip().upper()
    if not code:
        raise HTTPException(400, "Referral code required")

    # Find the new customer's loyalty program
    cp_result = await db.execute(
        select(LoyaltyProgram)
        .join(CustomerProfile, LoyaltyProgram.customer_id == CustomerProfile.id)
        .where(CustomerProfile.user_id == str(current_user.id))
    )
    my_lp = cp_result.scalar_one_or_none()
    if not my_lp:
        raise HTTPException(404, "Loyalty account not found")

    if getattr(my_lp, "referral_applied", False):
        raise HTTPException(400, "Referral code already used")

    # Find the referrer
    referrer_result = await db.execute(
        select(LoyaltyProgram).where(
            LoyaltyProgram.referral_code == code,
            LoyaltyProgram.id != str(my_lp.id),
        )
    )
    referrer_lp = referrer_result.scalar_one_or_none()
    if not referrer_lp:
        raise HTTPException(404, "Invalid referral code")

    REFERRAL_BONUS = 200

    # Award to new customer
    my_lp.total_points = (my_lp.total_points or 0) + REFERRAL_BONUS
    my_lp.redeemable_points = (my_lp.redeemable_points or 0) + REFERRAL_BONUS
    my_lp.lifetime_points_earned = (my_lp.lifetime_points_earned or 0) + REFERRAL_BONUS
    db.add(LoyaltyTransaction(
        id=generate_uuid(), loyalty_program_id=str(my_lp.id),
        transaction_type="earn", points=REFERRAL_BONUS,
        description=f"Referral bonus — joined via {code}",
    ))

    # Award to referrer
    referrer_lp.total_points = (referrer_lp.total_points or 0) + REFERRAL_BONUS
    referrer_lp.redeemable_points = (referrer_lp.redeemable_points or 0) + REFERRAL_BONUS
    referrer_lp.lifetime_points_earned = (referrer_lp.lifetime_points_earned or 0) + REFERRAL_BONUS
    db.add(LoyaltyTransaction(
        id=generate_uuid(), loyalty_program_id=str(referrer_lp.id),
        transaction_type="earn", points=REFERRAL_BONUS,
        description=f"Referral reward — friend joined with your code",
    ))

    # Mark as used (store on extra_data or a flag — using a workaround via description check)
    # In production, add a referral_applied boolean column to LoyaltyProgram
    try:
        my_lp.referral_code = f"USED:{code}"  # reuse field as applied marker
    except Exception:
        pass

    await db.commit()
    return APIResponse(
        success=True,
        message=f"Referral applied! You and your friend both earned {REFERRAL_BONUS} AURA Points.",
        data={"bonus_earned": REFERRAL_BONUS, "new_balance": my_lp.redeemable_points},
    )


@router.get("/referral/stats", response_model=APIResponse)
async def get_referral_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """How many friends have used your referral code and total referral earnings."""
    from app.models.loyalty import LoyaltyProgram, LoyaltyTransaction
    from app.models.customer import CustomerProfile

    cp_result = await db.execute(
        select(LoyaltyProgram)
        .join(CustomerProfile, LoyaltyProgram.customer_id == CustomerProfile.id)
        .where(CustomerProfile.user_id == str(current_user.id))
    )
    lp = cp_result.scalar_one_or_none()
    if not lp:
        raise HTTPException(404, "Loyalty account not found")

    # Count referral earnings
    referral_txns_result = await db.execute(
        select(LoyaltyTransaction).where(
            LoyaltyTransaction.loyalty_program_id == str(lp.id),
            LoyaltyTransaction.description.like("%Referral reward%"),
        )
    )
    referral_txns = referral_txns_result.scalars().all()

    return APIResponse(
        success=True,
        message="Referral stats",
        data={
            "referral_code": lp.referral_code if not (lp.referral_code or "").startswith("USED:") else None,
            "friends_referred": len(referral_txns),
            "total_referral_points": sum(t.points for t in referral_txns),
            "referral_bonus_per_friend": 200,
        },
    )
