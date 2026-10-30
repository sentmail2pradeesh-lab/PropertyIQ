"""Safely decode uploaded bytes into an image we can analyse.

Never trust the filename or the Content-Type header: we only accept a file
if Pillow can actually decode it as one of the allowed formats.
"""

import hashlib
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}  # RAW support arrives in milestone 6


class ImageValidationError(ValueError):
    """Raised when an upload is not a usable image."""


@dataclass(frozen=True)
class LoadedImage:
    rgb: np.ndarray  # H x W x 3, uint8, already rotated per EXIF
    format: str
    width: int
    height: int
    sha256: str


def load_image(data: bytes, max_pixels: int) -> LoadedImage:
    if not data:
        raise ImageValidationError("File is empty.")

    # Pillow raises DecompressionBombError above 2x this limit and warns above it.
    Image.MAX_IMAGE_PIXELS = max_pixels

    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()  # cheap integrity check; the object is unusable afterwards
        img = Image.open(io.BytesIO(data))
        img_format = img.format or ""
        if img_format not in ALLOWED_FORMATS:
            raise ImageValidationError(
                f"Unsupported format '{img_format or 'unknown'}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_FORMATS))}."
            )
        if img.width * img.height > max_pixels:
            raise ImageValidationError("Image resolution is too large.")

        # Cameras often store photos sideways and set an EXIF "Orientation" flag.
        # Apply it now, otherwise later room classification sees rotated rooms.
        img = ImageOps.exif_transpose(img)
        rgb = np.asarray(img.convert("RGB"))
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as exc:
        raise ImageValidationError("File could not be decoded as an image.") from exc

    height, width = rgb.shape[:2]
    return LoadedImage(
        rgb=rgb,
        format=img_format,
        width=width,
        height=height,
        sha256=hashlib.sha256(data).hexdigest(),
    )
