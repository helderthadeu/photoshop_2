"""Pre-built spatial image filters constructed on top of apply_convolution."""
import math

import numpy as np

from src.domain.conversion import to_grayscale, image_dimensions
from src.domain.convolution import apply_convolution, pad_image
from src.domain.types import ImageMatrix


def apply_median_filter(image: ImageMatrix | np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Replace each pixel with the median of its neighbourhood.

    Args:
        image: Input image as ImageMatrix or NumPy array.
        kernel_size: Side length of the square neighbourhood (must be odd).

    Returns:
        Filtered image as a uint8 NumPy array.

    Raises:
        ValueError: If kernel_size is even.
    """
    _require_odd(kernel_size)

    gray = to_grayscale(image).astype(np.uint8)
    padding = kernel_size // 2
    padded = pad_image(gray, padding)
    image_height, image_width = image_dimensions(gray)

    result_rows = []

    for row in range(image_height):
        row_data = []
        for col in range(image_width):
            median_value = _median_of_neighbourhood(padded, row, col, kernel_size)
            row_data.append(median_value)
        result_rows.append(row_data)

    return np.array(result_rows, dtype=np.uint8)


def apply_average_filter(image: ImageMatrix | np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Replace each pixel with the mean of its neighbourhood.

    Args:
        image: Input image as ImageMatrix or NumPy array.
        kernel_size: Side length of the square neighbourhood (must be odd).

    Returns:
        Filtered image as a uint32 NumPy array.

    Raises:
        ValueError: If kernel_size is even.
    """
    _require_odd(kernel_size)

    weight = 1.0 / kernel_size ** 2
    kernel = []

    for _ in range(kernel_size):
        row = []
        for _ in range(kernel_size):
            row.append(weight)
        kernel.append(row)

    return apply_convolution(image, kernel)


def apply_laplacian_filter(
    image: ImageMatrix | np.ndarray,
    kernel_size: int = 3,
    sigma: float = 1.0,
) -> np.ndarray:
    """Apply a Laplacian-of-Gaussian (LoG) filter.

    Args:
        image: Input image as ImageMatrix or NumPy array.
        kernel_size: Side length of the LoG kernel (must be odd).
        sigma: Standard deviation of the Gaussian component.

    Returns:
        Filtered image as a uint32 NumPy array.

    Raises:
        ValueError: If kernel_size is even or larger than the image.
    """
    _require_odd(kernel_size)
    kernel = _build_log_kernel(kernel_size, sigma)
    return apply_convolution(image, kernel)


def apply_derivative_filter(
    image: ImageMatrix | np.ndarray,
    kernel_size: int = 3,
    direction: str = "x",
) -> np.ndarray:
    """Apply a directional derivative (Sobel-like) filter.

    Args:
        image: Input image as ImageMatrix or NumPy array.
        kernel_size: Side length of the kernel (must be odd).
        direction: "x" for horizontal gradient, "y" for vertical.

    Returns:
        Filtered image as a uint32 NumPy array.

    Raises:
        ValueError: If kernel_size is even, direction is invalid, or kernel
                    is larger than the image.
    """
    _require_odd(kernel_size)
    kernel = _build_derivative_kernel(kernel_size, direction)
    return apply_convolution(image, kernel)


def apply_gaussian_filter(image: ImageMatrix | np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply a distance-weighted Gaussian blur.

    Args:
        image: Input image as ImageMatrix or NumPy array.
        kernel_size: Side length of the kernel (must be odd).

    Returns:
        Filtered image as a uint32 NumPy array.

    Raises:
        ValueError: If kernel_size is even or larger than the image.
    """
    _require_odd(kernel_size)
    kernel = _build_gaussian_kernel(kernel_size)
    return apply_convolution(image, kernel)


# --- Private kernel builders ---

def _build_log_kernel(kernel_size: int, sigma: float) -> list[list[float]]:
    """Build a Laplacian-of-Gaussian kernel and normalise its centre weight."""
    padding = kernel_size // 2
    kernel: list[list[float]] = []
    total = 0.0

    for y in range(-padding, padding + 1):
        row = []
        for x in range(-padding, padding + 1):
            gauss_term = (x * x + y * y) / (2 * sigma * sigma)
            value = -(1 / (math.pi * sigma ** 4)) * (1 - gauss_term) * math.exp(-gauss_term)
            row.append(value)
            total += value
        kernel.append(row)

    centre = kernel[padding][padding]
    kernel[padding][padding] = -(total - centre)

    return kernel


def _build_derivative_kernel(kernel_size: int, direction: str) -> list[list[float]]:
    """Build a Sobel-style derivative kernel along x or y."""
    if direction.lower() not in ("x", "y"):
        raise ValueError(f"Invalid direction '{direction}'. Choose 'x' or 'y'.")

    padding = kernel_size // 2
    kernel: list[list[float]] = []

    for y in range(-padding, padding + 1):
        row = []
        for x in range(-padding, padding + 1):
            if direction.lower() == "x":
                value = 0.0 if x == 0 else (x / abs(x)) * (2.0 if y == 0 else 1.0)
            else:
                value = 0.0 if y == 0 else (y / abs(y)) * (2.0 if x == 0 else 1.0)
            row.append(value)
        kernel.append(row)

    return kernel


def _build_gaussian_kernel(kernel_size: int) -> list[list[float]]:
    """Build a kernel where each weight is the Euclidean distance from the centre."""
    padding = kernel_size // 2
    kernel: list[list[float]] = []

    for y in range(-padding, padding + 1):
        row = []
        for x in range(-padding, padding + 1):
            distance = math.sqrt(x * x + y * y)
            row.append(distance)
        kernel.append(row)

    return kernel


def _median_of_neighbourhood(
    padded: list[list],
    row: int,
    col: int,
    kernel_size: int,
) -> int:
    neighbourhood = []

    for ki in range(kernel_size):
        for kj in range(kernel_size):
            neighbourhood.append(padded[row + ki][col + kj])

    neighbourhood.sort()
    return neighbourhood[(kernel_size * kernel_size + 1) // 2]


def _require_odd(kernel_size: int) -> None:
    if kernel_size % 2 == 0:
        raise ValueError(f"Kernel size must be odd, got {kernel_size}.")
