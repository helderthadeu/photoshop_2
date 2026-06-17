"""Histogram computation for grayscale images.

Plotting lives in the GUI layer (gui/panels); this module only computes.
"""
import cv2
import numpy as np

from src.domain.types import ImageMatrix

_INTENSITY_LEVELS = 256


def generate_histogram(image: ImageMatrix | np.ndarray) -> list[int]:
    """Count pixel occurrences for each intensity level [0, 255].

    Args:
        image: Grayscale ImageMatrix or NumPy array (colour is converted first).

    Returns:
        List of 256 counts indexed by intensity.
    """
    gray = _to_grayscale_uint8(image)
    histogram = [0] * _INTENSITY_LEVELS

    for row in gray:
        for pixel in row:
            histogram[_clamp_to_byte(pixel)] += 1

    return histogram


def render_histogram_image(
    histogram: list[int],
    width: int = 256,
    height: int = 200,
) -> ImageMatrix:
    """Render a histogram as a grayscale bar chart (white bars on black).

    Produces a saveable image so a histogram can be written to a PGM sink.

    Args:
        histogram: 256 frequency counts from generate_histogram.
        width: Output width in pixels (bins are mapped across it).
        height: Output height in pixels.

    Returns:
        An ImageMatrix of shape height×width with values 0 (background) or 255.
    """
    image: ImageMatrix = []
    for _ in range(height):
        image.append([0] * width)

    peak = max(histogram) if histogram else 0
    if peak == 0:
        return image

    bins = len(histogram)
    for column in range(width):
        count = histogram[column * bins // width]
        bar_height = round(count / peak * (height - 1))
        for row in range(height - bar_height, height):
            image[row][column] = 255

    return image


def _to_grayscale_uint8(image: ImageMatrix | np.ndarray) -> np.ndarray:
    array = np.array(image)
    if array.ndim == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    return array


def _clamp_to_byte(value: int | float) -> int:
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)
