"""Gemini Vision service for detecting grocery items from photos."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..config import settings
from ..schemas import PantryItemCreate

if TYPE_CHECKING:
    from google.genai import Client

log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a grocery detection assistant. Analyze the provided image and "
    "identify all grocery or food items visible. The image may be a receipt, "
    "a photo of food items, or a pantry shelf.\n\n"
    "For each item detected, return:\n"
    "- name: the grocery item name in lowercase. Include descriptors that "
    "change WHAT the item is: preparation (sliced, diced, shredded), "
    "texture (extra firm, creamy), cut (breast, thigh, fillet), sub-type "
    "(deli, smoked, aged), and form (whole wheat, sourdough). "
    "Examples: 'sliced turkey breast', 'extra firm tofu', 'sliced gouda "
    "cheese', 'whole wheat bread', 'extra virgin olive oil'.\n"
    "OMIT descriptors that do NOT change the item identity: size (large, "
    "small, medium), organic/conventional, brand names, origin (hass, "
    "fuji), and marketing terms. Put these in the notes field instead. "
    "Examples: 'large hass avocado' → name 'avocado', 'organic banana' "
    "→ name 'banana'.\n"
    "- quantity: numeric quantity if visible (null otherwise)\n"
    "- unit: unit of measurement if visible (null otherwise)\n"
    "- category: one of produce, dairy, meat, seafood, bakery, frozen, "
    "canned, dry goods, beverages, snacks, condiments, spices, or other\n"
    "- notes: any extra detail like brand (null otherwise)\n\n"
    "If no grocery items are detected, return an empty list."
)


class VisionAnalysisError(Exception):
    """Raised when the Gemini Vision API call fails."""


_client: Client | None = None
_client_initialized = False


def _get_client() -> Client | None:
    """Lazily initialize the Gemini client. Returns None if unavailable."""
    global _client, _client_initialized
    if _client_initialized:
        return _client
    _client_initialized = True

    if not settings.gemini_api_key:
        log.info("GEMINI_API_KEY not set — vision analysis disabled")
        return None

    try:
        from google import genai

        _client = genai.Client(api_key=settings.gemini_api_key)
        log.info("Gemini client initialized (model=%s)", settings.gemini_model)
        return _client
    except ImportError:
        log.warning("google-genai SDK not installed — vision analysis disabled")
        return None


async def analyze_image(image_bytes: bytes, mime_type: str) -> list[PantryItemCreate] | None:
    """Analyze an image and return detected grocery items.

    Returns None if the Gemini client is not configured.
    Raises VisionAnalysisError on API failures.
    """
    client = _get_client()
    if client is None:
        return None

    from google.genai import types

    try:
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(text=SYSTEM_PROMPT),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[PantryItemCreate],
            ),
        )
    except Exception as exc:
        raise VisionAnalysisError(f"Gemini API call failed: {exc}") from exc

    import json

    try:
        raw = json.loads(response.text)
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        raise VisionAnalysisError(f"Failed to parse Gemini response: {exc}") from exc

    return [PantryItemCreate.model_validate(item) for item in raw]
