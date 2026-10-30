"""Classical computer-vision quality checks.

No AI model here on purpose: blur and exposure are measurable with simple
maths, run in milliseconds, cost nothing and give the same answer every time.
We only reach for LLMs where rules can't do the job.
"""

import cv2
import numpy as np

from app.core.config import Settings
from app.schemas.image_analysis import BlurResult, ExposureResult, ExposureVerdict

ANALYZER_VERSION = "cv-quality-0.1.0"

SHADOW_LEVEL = 5  # luminance <= 5 counts as crushed black
HIGHLIGHT_LEVEL = 250  # luminance >= 250 counts as blown-out white


def to_analysis_gray(rgb: np.ndarray, max_side: int) -> np.ndarray:
    """Grayscale copy, downscaled so the longest side is at most `max_side`.

    Laplacian variance depends on resolution, so normalising size keeps one
    threshold meaningful across cameras.
    """
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    scale = max_side / max(h, w)
    if scale < 1:
        gray = cv2.resize(gray, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return gray


def measure_blur(gray: np.ndarray, threshold: float) -> BlurResult:
    """Variance of the Laplacian: sharp images have strong edges, so the
    second-derivative response varies a lot. Blurry images are 'flat'."""
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return BlurResult(
        laplacian_variance=round(variance, 2),
        threshold=threshold,
        is_blurry=variance < threshold,
    )


def measure_exposure(gray: np.ndarray, settings: Settings) -> ExposureResult:
    total = gray.size
    mean = float(gray.mean())
    shadows_pct = float(np.count_nonzero(gray <= SHADOW_LEVEL)) / total * 100
    highlights_pct = float(np.count_nonzero(gray >= HIGHLIGHT_LEVEL)) / total * 100

    warn = settings.clipping_warn_pct
    if shadows_pct >= warn and highlights_pct >= warn:
        verdict = ExposureVerdict.HIGH_CONTRAST
    elif mean < settings.underexposed_mean:
        verdict = ExposureVerdict.UNDEREXPOSED
    elif mean > settings.overexposed_mean:
        verdict = ExposureVerdict.OVEREXPOSED
    else:
        verdict = ExposureVerdict.WELL_EXPOSED

    return ExposureResult(
        mean_brightness=round(mean, 2),
        shadows_clipped_pct=round(shadows_pct, 2),
        highlights_clipped_pct=round(highlights_pct, 2),
        verdict=verdict,
    )


def describe_issues(
    blur: BlurResult, exposure: ExposureResult, clipping_warn_pct: float
) -> list[str]:
    issues: list[str] = []
    if blur.is_blurry:
        issues.append("Image appears blurry or out of focus.")
    messages = {
        ExposureVerdict.UNDEREXPOSED: "Image is underexposed (too dark).",
        ExposureVerdict.OVEREXPOSED: "Image is overexposed (too bright).",
        ExposureVerdict.HIGH_CONTRAST: (
            "Both shadows and highlights are clipped - typical of bright windows; "
            "may need HDR/bracket blending."
        ),
    }
    if exposure.verdict in messages:
        issues.append(messages[exposure.verdict])
    elif exposure.highlights_clipped_pct >= clipping_warn_pct:
        # Average brightness can look fine while a window is completely blown out.
        issues.append(
            f"{exposure.highlights_clipped_pct:.1f}% of pixels are blown out "
            "(often windows) - check the outdoor view is preserved."
        )
    elif exposure.shadows_clipped_pct >= clipping_warn_pct:
        issues.append(f"{exposure.shadows_clipped_pct:.1f}% of pixels are crushed to black.")
    return issues
