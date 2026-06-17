"""Image type-normalisation helpers shared by the processing algorithms.

NOTE: cv2 is used here only for BGR→gray conversion. If the course forbids
ready-made methods, replace cvtColor with a hand-written luminance conversion.
"""
import cv2
import numpy as np

from src.domain.types import ImageMatrix


def to_grayscale(image: ImageMatrix | np.ndarray) -> np.ndarray:
    """Normalise any supported image type to an int32 grayscale NumPy array.

    Accepts an ImageMatrix, a BGR NumPy array, or a grayscale NumPy array.
    """
    if isinstance(image, list):
        return np.array(image, dtype=np.int32)
    if image.ndim == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.int32)
    return image.astype(np.int32)


def image_dimensions(image: ImageMatrix | np.ndarray) -> tuple[int, int]:
    """Return (height, width) for either an ImageMatrix or a NumPy array."""
    if isinstance(image, list):
        return len(image), (len(image[0]) if image else 0)
    return image.shape[:2]
