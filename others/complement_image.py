"""Complement (negative) operation for grayscale images."""
from models.models import ImageMatrix


def invert_image(matrix: ImageMatrix) -> ImageMatrix:
    """Return the photographic negative of a grayscale image.

    Each pixel value v is mapped to 255 - v.

    Args:
        matrix: Input 8-bit grayscale ImageMatrix.

    Returns:
        New ImageMatrix with inverted pixel intensities.
    """
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0
    result: ImageMatrix = []

    for row in range(height):
        row_data = []
        for col in range(width):
            row_data.append(255 - matrix[row][col])
        result.append(row_data)

    return result
