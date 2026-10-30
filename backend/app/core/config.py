"""Application settings, loaded from environment variables / .env.

Every tunable value lives here so nothing is hardcoded in services.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PROPERTYIQ_",
        extra="ignore",
    )

    app_name: str = "PropertyIQ API"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    # Upload limits
    max_upload_mb: int = 25
    max_image_pixels: int = 60_000_000  # ~60 MP; guards against decompression bombs

    # Analysis is done on a resized copy so thresholds behave the same for
    # a 2 MP phone photo and a 45 MP DSLR photo.
    analysis_max_side_px: int = 1024

    # Quality thresholds (tuned later against a labelled evaluation set)
    blur_threshold: float = 100.0
    underexposed_mean: float = 70.0
    overexposed_mean: float = 190.0
    clipping_warn_pct: float = 5.0

    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
