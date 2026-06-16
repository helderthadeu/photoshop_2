"""Histogram computation and matching for grayscale images.

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


def normalize_histogram(histogram: list[int]) -> list[float]:
    """Convert a frequency histogram to a probability distribution.

    Args:
        histogram: Raw frequency counts from generate_histogram.

    Returns:
        List of 256 floats that sum to 1.0 (or all zeros if histogram is empty).
    """
    total = sum(histogram)
    if total == 0:
        return [0.0] * len(histogram)

    normalized = []
    for count in histogram:
        normalized.append(count / total)

    return normalized


def match_histograms(
    source: ImageMatrix | np.ndarray,
    target: ImageMatrix | np.ndarray,
) -> ImageMatrix | np.ndarray:
    """Remap source image intensities to match the target histogram.

    Args:
        source: Image whose histogram will be transformed.
        target: Image providing the reference histogram.

    Returns:
        Transformed image in the same format as source (list or ndarray).
    """
    source_cdf = _compute_cdf(normalize_histogram(generate_histogram(source)))
    target_cdf = _compute_cdf(normalize_histogram(generate_histogram(target)))
    mapping = _build_intensity_map(source_cdf, target_cdf)

    gray = _to_grayscale_uint8(source)
    matched = []

    for row in gray:
        matched_row = []
        for pixel in row:
            matched_row.append(mapping[_clamp_to_byte(pixel)])
        matched.append(matched_row)

    if isinstance(source, np.ndarray):
        return np.array(matched, dtype=np.uint8)
    return matched


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


def _compute_cdf(normalized: list[float]) -> list[float]:
    cumulative = []
    total = 0.0

    for probability in normalized:
        total += probability
        cumulative.append(total)

    return cumulative


def _build_intensity_map(source_cdf: list[float], target_cdf: list[float]) -> list[int]:
    mapping: list[int] = [0] * _INTENSITY_LEVELS
    target_idx = 0

    for source_idx in range(_INTENSITY_LEVELS):
        while target_idx < _INTENSITY_LEVELS - 1 and target_cdf[target_idx] < source_cdf[source_idx]:
            target_idx += 1

        if target_idx == 0:
            mapping[source_idx] = 0
            continue

        prev_distance = abs(source_cdf[source_idx] - target_cdf[target_idx - 1])
        curr_distance = abs(source_cdf[source_idx] - target_cdf[target_idx])

        if prev_distance < curr_distance:
            mapping[source_idx] = target_idx - 1
        else:
            mapping[source_idx] = target_idx

    return mapping
