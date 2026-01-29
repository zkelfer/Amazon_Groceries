import logging

from fastapi import APIRouter, HTTPException, UploadFile

from ..schemas import PhotoUploadResponse
from ..services.vision import VisionAnalysisError, analyze_image

router = APIRouter(prefix="/api/photos", tags=["photos"])
log = logging.getLogger(__name__)

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(photo: UploadFile):
    """Upload a pantry photo for ingredient detection.

    Uses Gemini Vision to detect grocery items when configured.
    Falls back to a stub message when no API key is set.
    """
    # Validate MIME type
    if photo.content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{photo.content_type}'. "
            f"Accepted types: {', '.join(sorted(_ALLOWED_MIME_TYPES))}",
        )

    image_bytes = await photo.read()

    # Validate file size
    if len(image_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large ({len(image_bytes) / 1024 / 1024:.1f} MB). "
            f"Maximum size is {_MAX_FILE_SIZE / 1024 / 1024:.0f} MB.",
        )

    try:
        items = await analyze_image(image_bytes, photo.content_type)
    except VisionAnalysisError as exc:
        log.error("Vision analysis failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Not configured — return stub
    if items is None:
        return PhotoUploadResponse(
            message=(
                "Photo received. Gemini Vision integration is not yet configured. "
                "Please add items manually."
            ),
            items=[],
        )

    # Configured but nothing detected
    if not items:
        return PhotoUploadResponse(
            message=(
                "No grocery items detected in this image. "
                "Try a clearer photo of a receipt, food items, or pantry shelf."
            ),
            items=[],
        )

    return PhotoUploadResponse(
        message=f"Detected {len(items)} item{'s' if len(items) != 1 else ''} from photo.",
        items=items,
    )
