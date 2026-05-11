"""Skin Tone Analysis Service — Server-side analysis via Gemini Vision.

Feature 2: Hybrid approach — server runs full analysis, browser shows
MediaPipe live preview while waiting. Results stored in Beauty Passport.
"""
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)


SKINTONE_PROMPT = """You are an expert skin tone analyst for South Asian beauty. Analyze the face in this image and return ONLY valid JSON with these exact fields:

{
  "skin_tone": "Fair" | "Medium" | "Dusky" | "Deep",
  "undertone": "Warm" | "Cool" | "Neutral",
  "fitzpatrick_scale": 1-6,
  "skin_type": "Oily" | "Dry" | "Combination" | "Normal",
  "face_shape": "Oval" | "Round" | "Square" | "Heart" | "Diamond" | "Oblong",
  "recommended_hair_colors": ["color1", "color2", "color3"],
  "avoid_hair_colors": ["color1", "color2"],
  "recommended_lip_shades": ["shade1", "shade2", "shade3"],
  "recommended_skincare_services": ["service1", "service2"],
  "recommended_eye_makeup": "description",
  "products_to_avoid_ingredients": ["ingredient1", "ingredient2"],
  "personalized_message": "2-sentence personalized beauty insight for this skin tone",
  "confidence_score": 0.0-1.0
}

Be specific to South Asian skin tones. Only return the JSON object, no markdown."""


async def analyze_skin_tone(image_data: bytes, mime_type: str = "image/jpeg") -> dict:
    """Analyze skin tone from image bytes using Gemini Vision.

    Returns structured skin tone analysis with beauty recommendations.
    Falls back to a graceful error dict if AI is unavailable.
    """
    from app.config import settings

    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return await _analyze_with_gemini(image_data, mime_type)
    elif settings.OPENAI_API_KEY:
        return await _analyze_with_openai(image_data, mime_type)
    else:
        logger.warning("[SkinTone] No AI provider configured — returning mock analysis")
        return _mock_analysis()


async def _analyze_with_gemini(image_data: bytes, mime_type: str) -> dict:
    """Gemini Vision skin tone analysis."""
    import json
    import httpx
    from app.config import settings

    b64_image = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "contents": [{
            "parts": [
                {"text": SKINTONE_PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": b64_image}},
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 800,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


async def _analyze_with_openai(image_data: bytes, mime_type: str) -> dict:
    """OpenAI Vision skin tone analysis (fallback)."""
    import json
    import httpx
    from app.config import settings

    b64_image = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": SKINTONE_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        "max_tokens": 800,
        "temperature": 0.1,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        )
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _mock_analysis() -> dict:
    """Dev fallback when no AI key is configured."""
    return {
        "skin_tone": "Medium",
        "undertone": "Warm",
        "fitzpatrick_scale": 4,
        "skin_type": "Combination",
        "face_shape": "Oval",
        "recommended_hair_colors": ["Copper Brown", "Mahogany", "Chestnut"],
        "avoid_hair_colors": ["Platinum Blonde", "Ash Grey"],
        "recommended_lip_shades": ["Berry", "Terracotta", "Nude Pink"],
        "recommended_skincare_services": ["Vitamin C Facial", "Hydra Facial"],
        "recommended_eye_makeup": "Warm browns and golds complement your undertone beautifully",
        "products_to_avoid_ingredients": ["High alcohol content", "Heavy sulfates"],
        "personalized_message": (
            "Your Medium Warm skin tone glows beautifully with earthy, rich tones. "
            "A Vitamin C facial will address pigmentation and give you a radiant finish."
        ),
        "confidence_score": 0.0,
        "_dev_mode": True,
    }
