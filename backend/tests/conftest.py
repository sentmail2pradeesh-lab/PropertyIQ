"""Synthetic test images, so tests never depend on files on disk."""

import io

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def encode(rgb: np.ndarray, fmt: str = "JPEG") -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, format=fmt, quality=95)
    return buf.getvalue()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sharp_rgb() -> np.ndarray:
    """Mid-grey checkerboard: lots of hard edges, balanced brightness."""
    tile = np.kron([[1, 0] * 16, [0, 1] * 16] * 12, np.ones((20, 20)))
    gray = (tile * 120 + 70).astype(np.uint8)  # values 70 and 190 -> mean 130
    return np.stack([gray] * 3, axis=-1)


@pytest.fixture
def blurry_rgb(sharp_rgb: np.ndarray) -> np.ndarray:
    return cv2.GaussianBlur(sharp_rgb, (51, 51), 15)


@pytest.fixture
def dark_rgb() -> np.ndarray:
    return np.full((400, 600, 3), 25, dtype=np.uint8)


@pytest.fixture
def bright_rgb() -> np.ndarray:
    return np.full((400, 600, 3), 225, dtype=np.uint8)
