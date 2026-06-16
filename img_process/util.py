"""Low-level array utilities used internally by the image processing pipeline."""
import cv2
import numpy as np

from models.models import ImageMatrix


def pad_image(
    image: ImageMatrix | np.ndarray,
    row_padding: int,
    col_padding: int = 0,
    fill_value: int = 255,
) -> list[list]:
    """Surround an image with a constant-value border.

    Args:
        image: 2-D image as ImageMatrix or grayscale NumPy array.
        row_padding: Rows of fill added to top and bottom.
        col_padding: Columns of fill added to left and right.
                     Defaults to row_padding when 0.
        fill_value: Border pixel value (default 255 — white).

    Returns:
        2-D list of shape (H + 2*row_padding) × (W + 2*col_padding).
    """
    col_padding = row_padding if col_padding == 0 else col_padding

    height = len(image)
    width = len(image[0]) if height > 0 else 0
    padded_width = col_padding + width + col_padding

    fill_row = [fill_value] * padded_width
    result: list[list] = []

    for _ in range(row_padding):
        result.append(fill_row[:])

    for row in image:
        padded_row = [fill_value] * col_padding + list(row) + [fill_value] * col_padding
        result.append(padded_row)

    for _ in range(row_padding):
        result.append(fill_row[:])

    return result


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
