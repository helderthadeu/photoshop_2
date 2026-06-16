"""Core convolution engine for spatial image filters."""
import numpy as np

from img_process.util import pad_image, to_grayscale
from models.models import ImageMatrix


def apply_convolution(
    image: ImageMatrix | np.ndarray,
    kernel: list[list[float]],
) -> np.ndarray:
    """Apply a 2-D convolution kernel to a grayscale image.

    The image is converted to grayscale before processing when needed.
    Kernel dimensions must be odd and smaller than the image.

    Args:
        image: Input image as ImageMatrix or NumPy array (grayscale or BGR).
        kernel: 2-D list of kernel weights (both dimensions must be odd).

    Returns:
        Convolved image as a uint32 NumPy array.

    Raises:
        ValueError: If kernel dimensions are even or larger than the image.
    """
    kernel_height = len(kernel)
    kernel_width = len(kernel[0])

    grayscale = to_grayscale(image)
    image_height, image_width = grayscale.shape

    _validate_kernel(kernel_height, kernel_width, image_height, image_width)

    row_pad = kernel_height // 2
    col_pad = kernel_width // 2
    padded = pad_image(grayscale, row_pad, col_pad)

    result_rows = []

    for row in range(image_height):
        row_data = []
        for col in range(image_width):
            total = 0.0
            for ki in range(kernel_height):
                for kj in range(kernel_width):
                    total += padded[row + ki][col + kj] * kernel[ki][kj]
            row_data.append(total)
        result_rows.append(row_data)

    return np.array(result_rows, dtype=np.uint32)


def _validate_kernel(
    kernel_height: int,
    kernel_width: int,
    image_height: int,
    image_width: int,
) -> None:
    if kernel_height % 2 == 0 or kernel_width % 2 == 0:
        raise ValueError("Kernel dimensions must be odd.")
    if kernel_height > image_height or kernel_width > image_width:
        raise ValueError("Kernel must be smaller than the image.")
