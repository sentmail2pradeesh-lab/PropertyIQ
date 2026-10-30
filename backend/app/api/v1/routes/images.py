from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.schemas.image_analysis import ImageAnalysisResponse, ImageMetadata
from app.services.image_loader import ImageValidationError, load_image
from app.services.image_quality import (
    ANALYZER_VERSION,
    describe_issues,
    measure_blur,
    measure_exposure,
    to_analysis_gray,
)

router = APIRouter(prefix="/images", tags=["images"])


# A plain `def` (not `async def`) on purpose: OpenCV work is CPU-bound, and
# FastAPI runs sync endpoints in a thread pool so they don't block the event loop.
@router.post(
    "/analyze",
    response_model=ImageAnalysisResponse,
    summary="Run quality checks (blur, exposure) on a single image",
)
def analyze_image(
    file: Annotated[UploadFile, File(description="JPG, PNG or WEBP photo")],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ImageAnalysisResponse:
    # Read at most limit+1 bytes so an oversized upload is rejected without
    # loading the whole thing into memory.
    data = file.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_mb} MB limit.",
        )

    try:
        image = load_image(data, max_pixels=settings.max_image_pixels)
    except ImageValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    gray = to_analysis_gray(image.rgb, settings.analysis_max_side_px)
    blur = measure_blur(gray, settings.blur_threshold)
    exposure = measure_exposure(gray, settings)

    return ImageAnalysisResponse(
        metadata=ImageMetadata(
            filename=file.filename or "upload",
            format=image.format,
            width=image.width,
            height=image.height,
            file_size_bytes=len(data),
            sha256=image.sha256,
        ),
        blur=blur,
        exposure=exposure,
        issues=describe_issues(blur, exposure, settings.clipping_warn_pct),
        analyzer_version=ANALYZER_VERSION,
    )
