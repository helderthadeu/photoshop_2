"""Image loading and ImageMatrix↔NumPy conversion. cv2 is confined to this module."""
from pathlib import Path

import cv2
import numpy as np

from src.domain.types import ImageMatrix


def load_image(path: str | Path) -> np.ndarray:
    """Load an image from disk and convert it from BGR to RGB.

    Args:
        path: Path to any image format supported by OpenCV.

    Returns:
        RGB NumPy array (H × W × 3).

    Raises:
        FileNotFoundError: If no file exists at path.
    """
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Image file not found: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def image_matrix_to_numpy(matrix: ImageMatrix) -> np.ndarray:
    """Convert an ImageMatrix to a uint8 grayscale NumPy array."""
    return np.array(matrix, dtype=np.uint8)


def numpy_to_image_matrix(array: np.ndarray) -> ImageMatrix:
    """Convert a NumPy array to an ImageMatrix (colour is converted to gray first)."""
    if array.ndim == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    return array.tolist()
