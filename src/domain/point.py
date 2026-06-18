"""Point-wise image processing operations that work directly on ImageMatrix."""
from src.domain.types import ImageMatrix

_MAX_PIXEL = 255
_MIN_PIXEL = 0


def adjust_brightness(matrix: ImageMatrix, bias: int) -> ImageMatrix:
    """Shift every pixel intensity by a constant bias, clamping to [0, 255].

    Args:
        matrix: Input 8-bit grayscale ImageMatrix.
        bias: Value added to each pixel (positive = brighter, negative = darker).

    Returns:
        New ImageMatrix with adjusted brightness.
    """
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0
    result: ImageMatrix = []

    for row in range(height):
        row_data = []
        for col in range(width):
            # Cast to a Python int first: upstream blocks emit uint8 NumPy
            # arrays, where `pixel + bias` would wrap on overflow (so +100%
            # looped back to the original) or reject a negative bias outright.
            pixel = int(matrix[row][col])
            new_value = max(_MIN_PIXEL, min(_MAX_PIXEL, pixel + bias))
            row_data.append(new_value)
        result.append(row_data)

    return result


def apply_threshold(matrix: ImageMatrix, threshold: int) -> ImageMatrix:
    """Binarise a grayscale image using a fixed intensity threshold.

    Pixels at or above threshold become 255; those below become 0.

    Args:
        matrix: Input 8-bit grayscale ImageMatrix.
        threshold: Cut-off intensity value in [0, 255].

    Returns:
        New binary ImageMatrix (values are 0 or 255).
    """
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0
    result: ImageMatrix = []

    for row in range(height):
        row_data = []
        for col in range(width):
            pixel = _MAX_PIXEL if matrix[row][col] >= threshold else _MIN_PIXEL
            row_data.append(pixel)
        result.append(row_data)

    return result
