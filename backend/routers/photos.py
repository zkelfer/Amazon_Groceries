from fastapi import APIRouter, UploadFile

from ..schemas import PantryItemCreate, PhotoUploadResponse

router = APIRouter(prefix="/api/photos", tags=["photos"])


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(photo: UploadFile):
    """Upload a pantry photo for ingredient detection.

    Currently stubbed — returns a message prompting manual entry.
    When an Anthropic API key is configured, this will use Claude Vision
    to detect items in the photo.
    """
    _ = await photo.read()  # consume upload

    # Stub: in a future version, send to Claude Vision API
    return PhotoUploadResponse(
        message="Photo received. Claude Vision integration is not yet configured. Please add items manually.",
        items=[],
    )
