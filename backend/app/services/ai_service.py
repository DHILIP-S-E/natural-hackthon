"""AURA AI Service — OpenAI GPT-4o integration with graceful fallback."""
import json
from typing import Optional
from app.config import settings

# ── Archetype data (shared with soulskin router) ──
ARCHETYPES = {
    "phoenix": {"name": "Phoenix", "emoji": "🔥", "color": "#E8611A", "element": "Fire",
                "description": "You are standing at the edge of something ending. You are not afraid of the fire."},
    "river": {"name": "River", "emoji": "🌊", "color": "#4A9FD4", "element": "Water",
              "description": "You are in flow. Something is shifting inside you."},
    "moon": {"name": "Moon", "emoji": "🌙", "color": "#7B68C8", "element": "Light",
             "description": "You are in a quiet phase. You need softness and gentle reflection."},
    "bloom": {"name": "Bloom", "emoji": "🌸", "color": "#E8A87C", "element": "Earth",
              "description": "You are growing. Something new is opening inside you."},
    "storm": {"name": "Storm", "emoji": "⛈️", "color": "#6B8FA6", "element": "Air",
              "description": "You carry weight today. You need grounding, not stimulation."},
}

_SOULSKIN_SYSTEM_PROMPT = """You are SOULSKIN — the world's first Emotion-to-Beauty Intelligence System.
A customer is about to receive a salon service. They answered 3 questions:
1. "What song describes your life right now?"
2. "What colour matches your mood today?"
3. "One word you want to FEEL when you leave."

Based on these answers AND the customer's beauty profile, you must:
1. Assign one archetype: phoenix | river | moon | bloom | storm
2. Write a 3-line poetic soul reading (each line on a new line)
3. Explain why this archetype fits today
4. Design the complete salon experience

Respond with ONLY valid JSON matching this exact structure:
{
  "archetype": "phoenix|river|moon|bloom|storm",
  "soul_reading": "Line 1\\nLine 2\\nLine 3",
  "archetype_reason": "Why this archetype fits today...",
  "service_protocol": {
    "primary_treatment": "...",
    "why_this_treatment": "...",
    "modified_technique": "...",
    "duration_change": "..."
  },
  "colour_direction": {
    "colour_story": "...",
    "symbolism": "...",
    "finish": "..."
  },
  "sensory_environment": {
    "aromatherapy": [{"scent": "...", "reason": "..."}],
    "lighting_start": "...",
    "lighting_end": "...",
    "music_arc": {"start_mood": "...", "end_mood": "..."},
    "temperature": "..."
  },
  "touch_protocol": {
    "massage_pressure": "light|medium|medium-to-deep|deep",
    "emotional_reason": "...",
    "scalp_ritual": "..."
  },
  "custom_formula": {
    "ingredients": [
      {"name": "...", "percentage": 30, "reason": "..."}
    ]
  },
  "stylist_script": {
    "opening": "...",
    "mid_service": "...",
    "closing": "...",
    "do_not_say": ["...", "...", "..."]
  },
  "mirror_monologue": "...",
  "private_life_note": "...",
  "look_created": "..."
}"""

_HOMECARE_SYSTEM_PROMPT = """You are AURA's AI beauty advisor. Generate a personalized home care plan.
Consider the customer's hair type, skin type, climate conditions, recent service, and SOULSKIN archetype.
Respond with ONLY valid JSON:
{
  "hair_routine": {
    "daily": ["step 1", "step 2"],
    "weekly": ["step 1"],
    "monthly": ["step 1"]
  },
  "skin_routine": {
    "daily": ["step 1", "step 2"],
    "weekly": ["step 1"],
    "monthly": ["step 1"]
  },
  "climate_adjustments": {"tip": "...", "reason": "..."},
  "archetype_rituals": {"ritual": "...", "frequency": "daily|weekly"},
  "product_recommendations": [
    {"product_name": "...", "usage": "...", "reason": "...", "estimated_price": 500}
  ],
  "dos": ["do 1", "do 2", "do 3"],
  "donts": ["dont 1", "dont 2", "dont 3"],
  "next_visit_recommendation": "Recommended service in X weeks",
  "next_visit_suggested_weeks": 4
}"""

_JOURNEY_SYSTEM_PROMPT = """You are AURA's Beauty Journey Planner. Create a personalized multi-month beauty roadmap.
Consider the customer's current hair/skin state, their primary beauty goal, and timeline.
Respond with ONLY valid JSON:
{
  "milestones": [
    {
      "week": 1,
      "milestone": "...",
      "salon_visit": {
        "recommended_service": "...",
        "estimated_cost": 1500,
        "why": "..."
      },
      "home_care": ["tip 1", "tip 2"],
      "expected_outcome": "..."
    }
  ],
  "expected_outcomes": {
    "week_4": "...",
    "week_8": "...",
    "week_12": "..."
  },
  "skin_projection": {"predicted_score": 80, "improvements": ["..."]},
  "estimated_total_cost": 15000,
  "ai_notes": "Personalized narrative about this journey..."
}"""

_QUALITY_SYSTEM_PROMPT = """You are AURA's quality feedback AI. Based on the service session data,
provide constructive, stylist-specific feedback. Be encouraging but honest.
Respond with a single paragraph of feedback text (not JSON)."""


def _get_ai_provider() -> str:
    """Determine which AI provider to use."""
    provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
    if provider == 'gemini' and settings.GEMINI_API_KEY:
        return 'gemini'
    if provider == 'openai' and settings.OPENAI_API_KEY:
        return 'openai'
    # Auto-detect: prefer whichever has a key
    if settings.GEMINI_API_KEY:
        return 'gemini'
    if settings.OPENAI_API_KEY:
        return 'openai'
    return 'none'


async def _call_gemini(messages: list, temperature: float = 0.7, max_tokens: int = 2000, json_mode: bool = True) -> str:
    """Call Google Gemini API. Returns raw text content."""
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash'),
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        ),
    )

    # Convert OpenAI-style messages to Gemini format
    system_parts = []
    chat_parts = []
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append(msg["content"])
        elif msg["role"] == "user":
            chat_parts.append({"role": "user", "parts": [msg["content"]]})
        elif msg["role"] == "assistant":
            chat_parts.append({"role": "model", "parts": [msg["content"]]})

    # Prepend system prompt to first user message if present
    if system_parts and chat_parts:
        chat_parts[0]["parts"] = ["\n".join(system_parts) + "\n\n" + chat_parts[0]["parts"][0]]

    response = await model.generate_content_async(
        [p for msg in chat_parts for p in msg["parts"]] if len(chat_parts) == 1
        else chat_parts,
    )
    return response.text


async def _call_openai(messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> dict:
    """AI JSON call — uses Gemini or OpenAI based on config. Returns parsed JSON dict."""
    provider = _get_ai_provider()

    if provider == 'gemini':
        try:
            content = await _call_gemini(messages, temperature, max_tokens, json_mode=True)
            return json.loads(content)
        except Exception as e:
            raise RuntimeError(f"Gemini call failed: {e}")

    if provider == 'openai':
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=20.0)
            response = await client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            raise RuntimeError(f"OpenAI call failed: {e}")

    raise RuntimeError("No AI provider configured (set GEMINI_API_KEY or OPENAI_API_KEY)")


async def _call_openai_text(messages: list, temperature: float = 0.7, max_tokens: int = 500) -> str:
    """AI text call — uses Gemini or OpenAI. Returns plain text."""
    provider = _get_ai_provider()

    if provider == 'gemini':
        try:
            return await _call_gemini(messages, temperature, max_tokens, json_mode=False)
        except Exception as e:
            raise RuntimeError(f"Gemini call failed: {e}")

    if provider == 'openai':
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=15.0)
            response = await client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI call failed: {e}")

    raise RuntimeError("No AI provider configured")


# ── Fallback functions (rule-based, used when OpenAI is unavailable) ──

def _fallback_soul_reading(colour: str, word: str, song: str = "") -> dict:
    """Rule-based archetype assignment from colour keywords."""
    colour_lower = (colour or "").lower()
    word_lower = (word or "").lower()

    if any(c in colour_lower for c in ["red", "orange", "fire", "crimson", "scarlet"]):
        archetype = "phoenix"
    elif any(c in colour_lower for c in ["blue", "aqua", "teal", "cyan", "navy"]):
        archetype = "river"
    elif any(c in colour_lower for c in ["purple", "violet", "lavender", "indigo", "lilac"]):
        archetype = "moon"
    elif any(c in colour_lower for c in ["pink", "peach", "coral", "gold", "yellow", "rose"]):
        archetype = "bloom"
    else:
        archetype = "storm"

    arch = ARCHETYPES[archetype]
    return {
        "archetype": archetype,
        "soul_reading": f"You chose the colour of {arch['element'].lower()} today.\nSomething in you is ready for {word_lower or 'change'}.\nLet this moment be the beginning.",
        "archetype_reason": f"Your colour '{colour}' and desire to feel '{word}' align with the {arch['name']} archetype — the energy of {arch['element'].lower()}.",
        "service_protocol": {
            "primary_treatment": f"Customized treatment aligned with {arch['name']} energy",
            "why_this_treatment": f"{arch['name']} archetype needs {arch['element'].lower()} energy in transformation",
            "modified_technique": f"Adjusted for {archetype} energy — {'bold and decisive' if archetype == 'phoenix' else 'gentle and grounding' if archetype == 'storm' else 'flowing and natural'}",
            "duration_change": "+10 minutes — creating space for transformation",
        },
        "colour_direction": {
            "colour_story": f"Inspired by your chosen colour: {colour}",
            "symbolism": f"Represents the {arch['element'].lower()} within — visible transformation",
            "finish": "A finish that reflects your inner state outward",
        },
        "sensory_environment": {
            "aromatherapy": [
                {"scent": "bergamot", "reason": "uplifts and energizes"},
                {"scent": "cedarwood" if archetype in ["storm", "moon"] else "ylang ylang", "reason": "grounds and stabilizes" if archetype in ["storm", "moon"] else "opens the heart"},
            ],
            "lighting_start": "warm amber 2700K",
            "lighting_end": "bright natural 4000K — emerging into clarity",
            "music_arc": {"start_mood": "contemplative", "end_mood": "empowered"},
            "temperature": "comfortable — letting your body relax into the experience",
        },
        "touch_protocol": {
            "massage_pressure": "medium" if archetype in ["bloom", "river"] else "medium-to-deep",
            "emotional_reason": f"{arch['name']} archetype benefits from {'gentle nurturing' if archetype in ['moon', 'bloom'] else 'grounding pressure'}",
            "scalp_ritual": "Begin with slow circular strokes at temples, work inward to crown",
        },
        "custom_formula": {
            "ingredients": [
                {"name": "Rosehip Oil", "percentage": 30, "reason": "Skin repair + emotional healing"},
                {"name": "Argan Oil", "percentage": 25, "reason": "Moisture + strength"},
                {"name": "Lavender Essential Oil", "percentage": 5, "reason": "Calms the nervous system"},
                {"name": "Keratin Protein", "percentage": 35, "reason": "Rebuilds structural bonds"},
                {"name": "Vitamin E", "percentage": 5, "reason": "Antioxidant protection"},
            ]
        },
        "stylist_script": {
            "opening": f"You chose '{colour}' — that tells me something beautiful about where you are right now.",
            "mid_service": "How are you feeling? We're halfway through your transformation.",
            "closing": "Look at that. That's not just a new look. That's who you've been becoming.",
            "do_not_say": ["You look tired", "Are you stressed?", "What happened to your hair?"],
        },
        "mirror_monologue": f"Today, {arch['name']} energy guided this transformation. The beauty was always there — we just let it show.",
        "private_life_note": f"Today I chose '{colour}' as my colour. I wanted to feel '{word}'. And I left feeling exactly that.",
        "look_created": f"A look designed for the {arch['name']} archetype — {arch['element']} energy made visible.",
    }


def _fallback_homecare(hair_type: str = "", skin_type: str = "", archetype: str = "") -> dict:
    """Rule-based homecare plan."""
    hair_tips = {
        "dry": {"daily": ["Apply leave-in conditioner", "Avoid heat styling"], "weekly": ["Deep conditioning mask"], "monthly": ["Protein treatment"]},
        "oily": {"daily": ["Use clarifying shampoo", "Avoid heavy oils"], "weekly": ["Apple cider vinegar rinse"], "monthly": ["Scalp detox"]},
    }
    skin_tips = {
        "dry": {"daily": ["Hyaluronic acid serum", "SPF 30+ sunscreen"], "weekly": ["Hydrating face mask"], "monthly": ["Professional facial"]},
        "oily": {"daily": ["Niacinamide serum", "Oil-free moisturizer"], "weekly": ["Clay mask"], "monthly": ["Deep cleansing facial"]},
    }
    return {
        "hair_routine": hair_tips.get(hair_type, hair_tips.get("dry", {})),
        "skin_routine": skin_tips.get(skin_type, skin_tips.get("dry", {})),
        "climate_adjustments": {"tip": "Adjust routine based on local humidity and UV levels", "reason": "Weather impacts hair and skin health"},
        "archetype_rituals": {"ritual": f"Begin each morning with 2 minutes of mindful breathing — {archetype or 'your'} archetype needs intentional starts", "frequency": "daily"},
        "product_recommendations": [
            {"product_name": "Gentle sulfate-free shampoo", "usage": "Every wash", "reason": "Preserves natural oils", "estimated_price": 450},
            {"product_name": "SPF 50 sunscreen", "usage": "Daily morning", "reason": "UV protection", "estimated_price": 350},
            {"product_name": "Argan oil serum", "usage": "Post-wash", "reason": "Adds moisture and shine", "estimated_price": 600},
        ],
        "dos": ["Use lukewarm water for hair wash", "Apply SPF daily even on cloudy days", "Stay hydrated — 8 glasses daily", "Get 7-8 hours sleep"],
        "donts": ["Avoid hot water on hair", "Don't skip sunscreen", "Avoid excessive heat styling", "Don't touch your face frequently"],
        "next_visit_recommendation": "Deep conditioning treatment recommended",
        "next_visit_suggested_weeks": 4,
    }


def _fallback_journey(goal: str = "", duration_weeks: int = 12, hair_damage: int = 3) -> dict:
    """Rule-based journey plan."""
    milestones = []
    for i in range(0, duration_weeks, max(duration_weeks // 4, 2)):
        week = i + 1
        phase = "Recovery" if i < duration_weeks // 3 else "Strengthening" if i < 2 * duration_weeks // 3 else "Maintenance"
        milestones.append({
            "week": week,
            "milestone": f"{phase} phase — Week {week}",
            "salon_visit": {
                "recommended_service": "Deep Protein Treatment" if phase == "Recovery" else "Hair Spa" if phase == "Strengthening" else "Gloss Treatment",
                "estimated_cost": 1500 if phase == "Recovery" else 1200,
                "why": f"Essential for {phase.lower()} phase of your beauty journey",
            },
            "home_care": [
                "Apply recommended hair mask twice weekly",
                "Follow your personalized home care routine",
                "Take progress photos for comparison",
            ],
            "expected_outcome": f"{'Reduced breakage' if phase == 'Recovery' else 'Improved texture' if phase == 'Strengthening' else 'Visible transformation'} by week {week}",
        })
    return {
        "milestones": milestones,
        "expected_outcomes": {
            "week_4": "Visible reduction in damage, improved scalp condition",
            "week_8": "Hair texture noticeably smoother, scalp balanced",
            f"week_{duration_weeks}": f"Target achieved: {goal or 'Overall hair health improvement'}",
        },
        "skin_projection": {"predicted_score": min(85, 60 + duration_weeks), "improvements": ["Hydration", "Texture", "Radiance"]},
        "estimated_total_cost": len(milestones) * 1500,
        "ai_notes": f"This {duration_weeks}-week journey is designed to achieve: {goal or 'comprehensive beauty improvement'}. Consistency is key — each salon visit builds on the previous one.",
    }


# ── Public API ──

async def generate_soul_reading(song: str, colour: str, word: str, customer_context: dict = None) -> dict:
    """Generate SOULSKIN soul reading. Falls back to rule-based if OpenAI unavailable."""
    if _get_ai_provider() == 'none':
        return {**_fallback_soul_reading(colour, word, song), "_ai_generated": False}

    ctx = customer_context or {}
    user_msg = f"Song: {song}\nColour: {colour}\nWord: {word}"
    if ctx:
        user_msg += f"\n\nCustomer context: {json.dumps(ctx)}"

    try:
        result = await _call_openai([
            {"role": "system", "content": _SOULSKIN_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ], temperature=0.8)
        # Validate archetype
        if result.get("archetype") not in ARCHETYPES:
            result["archetype"] = "bloom"
        result["_ai_generated"] = True
        return result
    except Exception:
        return {**_fallback_soul_reading(colour, word, song), "_ai_generated": False}


async def generate_homecare_plan(customer_profile: dict, archetype: str = None, climate_data: dict = None, service_done: str = None) -> dict:
    """Generate personalized home care plan."""
    if _get_ai_provider() == 'none':
        return {**_fallback_homecare(
            customer_profile.get("hair_type", ""),
            customer_profile.get("skin_type", ""),
            archetype or "",
        ), "_ai_generated": False}

    user_msg = f"Customer profile: {json.dumps(customer_profile)}"
    if archetype:
        user_msg += f"\nSOULSKIN archetype: {archetype}"
    if climate_data:
        user_msg += f"\nLocal climate: {json.dumps(climate_data)}"
    if service_done:
        user_msg += f"\nService just completed: {service_done}"

    try:
        result = await _call_openai([
            {"role": "system", "content": _HOMECARE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ], temperature=0.6)
        result["_ai_generated"] = True
        return result
    except Exception:
        return {**_fallback_homecare(
            customer_profile.get("hair_type", ""),
            customer_profile.get("skin_type", ""),
            archetype or "",
        ), "_ai_generated": False}


async def generate_journey_plan(customer_profile: dict, primary_goal: str, duration_weeks: int = 12) -> dict:
    """Generate personalized beauty journey plan."""
    if _get_ai_provider() == 'none':
        return {**_fallback_journey(
            primary_goal,
            duration_weeks,
            customer_profile.get("hair_damage_level", 3),
        ), "_ai_generated": False}

    user_msg = f"Customer: {json.dumps(customer_profile)}\nGoal: {primary_goal}\nDuration: {duration_weeks} weeks"

    try:
        result = await _call_openai([
            {"role": "system", "content": _JOURNEY_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ], temperature=0.6, max_tokens=3000)
        result["_ai_generated"] = True
        return result
    except Exception:
        return {**_fallback_journey(primary_goal, duration_weeks), "_ai_generated": False}


async def generate_quality_feedback(session_data: dict) -> str:
    """Generate AI feedback for a service session."""
    if _get_ai_provider() == 'none':
        score = session_data.get("overall_score", 75)
        if score >= 85:
            return "Excellent service delivery. SOP compliance and timing were both strong. Keep up the great work!"
        elif score >= 70:
            return "Good service overall. Consider paying more attention to timing consistency and ensure all SOP steps are followed completely."
        else:
            return "This session needs improvement. Review the SOP steps that were missed or rushed. Consider additional training on this service category."

    try:
        return await _call_openai_text([
            {"role": "system", "content": _QUALITY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Session data: {json.dumps(session_data)}"},
        ], temperature=0.5)
    except Exception:
        return "Quality feedback generation unavailable. Please review session details manually."
