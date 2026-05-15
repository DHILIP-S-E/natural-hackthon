"""Platform configuration endpoints — returns reference data the frontend needs."""
from datetime import datetime
from fastapi import APIRouter
from schemas.common import APIResponse

router = APIRouter(prefix="/config", tags=["Configuration"])

_CONSULTATION_OPTIONS = {
    "steps": ["Hair & Scalp", "Skin", "Allergies", "Visit Intent", "Health & Sign"],
    "hair_types": ["Straight", "Wavy", "Curly", "Coily"],
    "scalp_conditions": ["Normal", "Oily", "Dry", "Sensitive"],
    "skin_types": ["Oily", "Dry", "Combination", "Normal", "Sensitive"],
    "visit_goals": ["Maintain current look", "Try something new", "Special occasion", "Repair & restore"],
    "budgets": ["Budget", "Standard", "Premium"],
}

_SYSTEM_CONFIG = {
    "feature_toggles": [
        {
            "key": "soulskin_enabled",
            "label": "SOULSKIN Engine",
            "description": "AI-powered archetype-based beauty personality analysis",
            "enabled": True,
        },
        {
            "key": "smart_mirror_enabled",
            "label": "AI Smart Mirror",
            "description": "AR-powered virtual try-on for hairstyles and makeup",
            "enabled": True,
        },
    ],
    "default_operating_hours": [
        {"day": "Monday",    "open": "09:00", "close": "21:00"},
        {"day": "Tuesday",   "open": "09:00", "close": "21:00"},
        {"day": "Wednesday", "open": "09:00", "close": "21:00"},
        {"day": "Thursday",  "open": "09:00", "close": "21:00"},
        {"day": "Friday",    "open": "09:00", "close": "21:00"},
        {"day": "Saturday",  "open": "08:00", "close": "22:00"},
        {"day": "Sunday",    "open": "10:00", "close": "20:00"},
    ],
}

_FESTIVAL_DEFS = [
    {"month": 10, "day": 2,  "name": "Gandhi Jayanti",          "demand_multiplier": 1.3},
    {"month": 11, "day": 1,  "name": "Diwali Season",           "demand_multiplier": 2.2},
    {"month": 12, "day": 25, "name": "Christmas",               "demand_multiplier": 1.5},
    {"month": 12, "day": 31, "name": "New Year's Eve",          "demand_multiplier": 2.0},
    {"month": 1,  "day": 14, "name": "Pongal / Makar Sankranti","demand_multiplier": 1.8},
    {"month": 2,  "day": 14, "name": "Valentine's Day",         "demand_multiplier": 1.6},
    {"month": 3,  "day": 8,  "name": "Women's Day",             "demand_multiplier": 1.9},
]

_VOICE_LANGUAGES = [
    {"code": "en-IN", "api_code": "en", "label": "English"},
    {"code": "ta-IN", "api_code": "ta", "label": "Tamil"},
    {"code": "te-IN", "api_code": "te", "label": "Telugu"},
    {"code": "hi-IN", "api_code": "hi", "label": "Hindi"},
    {"code": "kn-IN", "api_code": "kn", "label": "Kannada"},
    {"code": "ml-IN", "api_code": "ml", "label": "Malayalam"},
]

_RBAC_MATRIX = {
    "roles": [
        "super_admin", "regional_manager", "franchise_owner",
        "salon_manager", "stylist", "customer",
    ],
    "capabilities": [
        "manage_staff", "view_reports", "run_soulskin", "manage_bookings",
        "view_customers", "manage_locations", "manage_config", "manage_rbac",
        "view_analytics", "manage_services",
    ],
    "permissions": {
        "super_admin": [
            "manage_staff", "view_reports", "run_soulskin", "manage_bookings",
            "view_customers", "manage_locations", "manage_config", "manage_rbac",
            "view_analytics", "manage_services",
        ],
        "regional_manager": [
            "manage_staff", "view_reports", "run_soulskin", "manage_bookings",
            "view_customers", "manage_locations", "view_analytics",
        ],
        "franchise_owner": [
            "manage_staff", "view_reports", "run_soulskin", "manage_bookings",
            "view_customers", "manage_locations", "view_analytics",
        ],
        "salon_manager": [
            "manage_staff", "view_reports", "run_soulskin", "manage_bookings",
            "view_customers", "view_analytics", "manage_services",
        ],
        "stylist":  ["run_soulskin", "view_customers", "manage_bookings"],
        "customer": ["manage_bookings", "run_soulskin"],
    },
}

_SOULSKIN_QUESTIONS = [
    {
        "key": "song",
        "emoji": "🎵",
        "question": "What song describes your life right now?",
        "placeholder": "e.g. Kesariya, Shape of You, Numb...",
    },
    {
        "key": "colour",
        "emoji": "🎨",
        "question": "What colour matches your mood today?",
        "placeholder": "e.g. Gold, Grey, Red, Blue...",
    },
    {
        "key": "word",
        "emoji": "💬",
        "question": "One word you want to FEEL when you leave?",
        "placeholder": "e.g. Free, Bold, Peace, Alive...",
    },
]

_SERVICE_FILTERS = [
    "All", "Hair Colour", "Keratin", "Facial", "Bridal Makeup",
    "Manicure", "Pedicure", "Head Massage", "Hair Cut",
]


@router.get("/consultation-options", response_model=APIResponse)
async def get_consultation_options():
    """Consultation form option lists (hair types, skin types, etc.)."""
    return APIResponse(success=True, data=_CONSULTATION_OPTIONS)


@router.get("/system", response_model=APIResponse)
async def get_system_config():
    """Platform-wide feature toggles and default operating hours."""
    return APIResponse(success=True, data=_SYSTEM_CONFIG)


@router.get("/festivals", response_model=APIResponse)
async def get_festivals():
    """Festival calendar with upcoming events and demand multipliers."""
    today = datetime.today().date()
    enriched = []
    for f in _FESTIVAL_DEFS:
        d = datetime(today.year, f["month"], f["day"]).date()
        if d <= today:
            d = datetime(today.year + 1, f["month"], f["day"]).date()
        enriched.append({**f, "days_away": (d - today).days})
    enriched.sort(key=lambda x: x["days_away"])
    return APIResponse(success=True, data={"upcoming": enriched[:4], "all": enriched})


@router.get("/voice-languages", response_model=APIResponse)
async def get_voice_languages():
    """Supported voice assistant languages."""
    return APIResponse(success=True, data={"languages": _VOICE_LANGUAGES})


@router.get("/rbac-matrix", response_model=APIResponse)
async def get_rbac_matrix():
    """Roles × capabilities permission matrix for RBAC display."""
    return APIResponse(success=True, data=_RBAC_MATRIX)


@router.get("/soulskin-questions", response_model=APIResponse)
async def get_soulskin_questions():
    """SOULSKIN flow question prompts."""
    return APIResponse(success=True, data={"questions": _SOULSKIN_QUESTIONS})


@router.get("/service-filters", response_model=APIResponse)
async def get_service_filters():
    """Available service filter chips for the salon map."""
    return APIResponse(success=True, data={"filters": _SERVICE_FILTERS})


@router.get("/platform-stats", response_model=APIResponse)
async def get_platform_stats():
    """Public platform statistics for the landing page."""
    return APIResponse(success=True, data={
        "salon_count": "750+",
        "ai_modules": "8",
        "user_roles": "6",
    })
