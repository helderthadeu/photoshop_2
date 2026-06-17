"""Pixel-wise absolute difference between two images."""
import numpy as np

from src.domain.types import ImageMatrix


def compute_grayscale_difference(image_a: ImageMatrix, image_b: ImageMatrix) -> ImageMatrix:
    """Return the absolute pixel-wise difference between two grayscale images.

    When images differ in size, only the overlapping region is compared and
    a warning is printed to stdout.

    Args:
        image_a: First grayscale ImageMatrix.
        image_b: Second grayscale ImageMatrix.

    Returns:
        ImageMatrix where each value is |image_a[r][c] - image_b[r][c]|.
    """
    height = min(len(image_a), len(image_b))
    width = min(len(image_a[0]), len(image_b[0]))

    _warn_if_sizes_differ(image_a, image_b, height, width)

    result: ImageMatrix = []

    for row in range(height):
        row_data = []
        for col in range(width):
            diff = abs(int(image_a[row][col]) - int(image_b[row][col]))
            row_data.append(diff)
        result.append(row_data)

    return result


def _warn_if_sizes_differ(
    image_a: ImageMatrix | np.ndarray,
    image_b: ImageMatrix | np.ndarray,
    cropped_height: int,
    cropped_width: int,
) -> None:
    if len(image_a) != len(image_b) or len(image_a[0]) != len(image_b[0]):
        print(
            f"Aviso: imagens com tamanhos diferentes. "
            f"Imagem A: ({len(image_a)}, {len(image_a[0])}), "
            f"Imagem B: ({len(image_b)}, {len(image_b[0])}). "
            f"Comparando região comum: {cropped_height}×{cropped_width}."
        )
