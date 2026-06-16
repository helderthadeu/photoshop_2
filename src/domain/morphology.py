"""Morphological operations for binary and grayscale images (stubs)."""
from src.domain.types import ImageMatrix


def apply_erosion(image: ImageMatrix, structuring_element: list[list[int]]) -> ImageMatrix:
    """Erode image using the given structuring element (not yet implemented)."""
    raise NotImplementedError("Erosion is not implemented yet.")


def apply_dilation(image: ImageMatrix, structuring_element: list[list[int]]) -> ImageMatrix:
    """Dilate image using the given structuring element (not yet implemented)."""
    raise NotImplementedError("Dilation is not implemented yet.")
