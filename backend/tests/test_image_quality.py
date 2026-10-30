"""Unit tests for the pure CV functions (no HTTP involved)."""

import numpy as np

from app.core.config import Settings
from app.schemas.image_analysis import ExposureVerdict
from app.services.image_quality import (
    describe_issues,
    measure_blur,
    measure_exposure,
    to_analysis_gray,
)

SETTINGS = Settings()


def gray(rgb: np.ndarray) -> np.ndarray:
    return to_analysis_gray(rgb, SETTINGS.analysis_max_side_px)


def test_sharp_image_is_not_blurry(sharp_rgb):
    assert not measure_blur(gray(sharp_rgb), SETTINGS.blur_threshold).is_blurry


def test_blurred_image_is_blurry(blurry_rgb):
    assert measure_blur(gray(blurry_rgb), SETTINGS.blur_threshold).is_blurry


def test_dark_image_is_underexposed(dark_rgb):
    assert measure_exposure(gray(dark_rgb), SETTINGS).verdict == ExposureVerdict.UNDEREXPOSED


def test_bright_image_is_overexposed(bright_rgb):
    assert measure_exposure(gray(bright_rgb), SETTINGS).verdict == ExposureVerdict.OVEREXPOSED


def test_window_scene_is_high_contrast():
    # Half pure black room, half blown-out window
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img[:, 300:] = 255
    assert measure_exposure(gray(img), SETTINGS).verdict == ExposureVerdict.HIGH_CONTRAST


def test_large_images_are_downscaled():
    big = np.zeros((3000, 4500, 3), dtype=np.uint8)
    assert max(to_analysis_gray(big, 1024).shape) == 1024


def test_blown_window_warns_even_when_average_is_fine(sharp_rgb):
    img = sharp_rgb.copy()
    img[100:300, 300:600] = 255  # bright window, rest of the room is normal
    g = gray(img)
    exposure = measure_exposure(g, SETTINGS)
    assert exposure.verdict == ExposureVerdict.WELL_EXPOSED
    issues = describe_issues(
        measure_blur(g, SETTINGS.blur_threshold), exposure, SETTINGS.clipping_warn_pct
    )
    assert any("blown out" in i for i in issues)
