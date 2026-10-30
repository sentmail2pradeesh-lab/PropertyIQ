"""Response models for image analysis.

Pydantic models are the API contract: FastAPI validates outgoing data against
them and uses them to generate the OpenAPI docs at /docs.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ExposureVerdict(StrEnum):
    WELL_EXPOSED = "well_exposed"
    UNDEREXPOSED = "underexposed"
    OVEREXPOSED = "overexposed"
    HIGH_CONTRAST = "high_contrast"  # both shadows and highlights clipped


class ImageMetadata(BaseModel):
    filename: str
    format: str = Field(description="Decoded format, e.g. JPEG, PNG, WEBP")
    width: int
    height: int
    file_size_bytes: int
    sha256: str = Field(description="Exact-duplicate fingerprint of the original bytes")


class BlurResult(BaseModel):
    laplacian_variance: float = Field(description="Higher = more edge detail = sharper")
    threshold: float
    is_blurry: bool


class ExposureResult(BaseModel):
    mean_brightness: float = Field(ge=0, le=255)
    shadows_clipped_pct: float = Field(ge=0, le=100, description="% pixels near pure black")
    highlights_clipped_pct: float = Field(ge=0, le=100, description="% pixels near pure white")
    verdict: ExposureVerdict


class ImageAnalysisResponse(BaseModel):
    metadata: ImageMetadata
    blur: BlurResult
    exposure: ExposureResult
    issues: list[str] = Field(description="Human-readable problems found")
    analyzer_version: str = Field(description="Bump when the algorithm or thresholds change")
