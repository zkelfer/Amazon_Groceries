import logging

from fastapi import APIRouter, HTTPException, UploadFile

from ..schemas import PhotoUploadResponse
from ..services.vision import VisionAnalysisError, analyze_image

router = APIRouter(prefix="/api/photos", tags=["photos"])
log = logging.getLogger(__name__)

_ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "image/heic", "image/heif",
}
# HEIC/HEIF need conversion to JPEG for Gemini (it doesn't accept HEIC)
_NEEDS_CONVERSION = {"image/heic", "image/heif"}
_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(photo: UploadFile):
    """Upload a pantry photo for ingredient detection.

    Uses Gemini Vision to detect grocery items when configured.
    Falls back to a stub message when no API key is set.
    """
    content_type = photo.content_type or "application/octet-stream"

    # Validate MIME type
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{content_type}'. "
            f"Accepted types: JPEG, PNG, WebP, GIF, HEIC.",
        )

    # Read file in chunks to enforce size limit before loading fully into memory
    chunks = []
    total_size = 0
    while True:
        chunk = await photo.read(64 * 1024)  # 64 KB chunks
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > _MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Image too large (>{_MAX_FILE_SIZE / 1024 / 1024:.0f} MB). "
                f"Maximum size is {_MAX_FILE_SIZE / 1024 / 1024:.0f} MB.",
            )
        chunks.append(chunk)
    image_bytes = b"".join(chunks)
    mime_type = content_type

    # Convert HEIC/HEIF to JPEG for Gemini compatibility
    if content_type in _NEEDS_CONVERSION:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=90)
            image_bytes = buf.getvalue()
            mime_type = "image/jpeg"
        except Exception as exc:
            log.warning("HEIC conversion failed: %s", exc)
            raise HTTPException(
                status_code=415,
                detail="Could not process HEIC/HEIF image. Try converting to JPEG first.",
            ) from exc

    try:
        items = await analyze_image(image_bytes, mime_type)
    except VisionAnalysisError as exc:
        log.error("Vision analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Image analysis failed. Please try again later.",
        ) from exc

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
