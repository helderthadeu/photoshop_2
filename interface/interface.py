"""Image I/O, display, and format-conversion utilities for the PSE-Image pipeline."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import cv2
import matplotlib.pyplot as plt
import numpy as np

from typing import Optional

from models.models import ImageMatrix

FilePath = Optional[str]


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


def display_image(image: np.ndarray, title: str = "", cmap: str = "viridis") -> None:
    """Show a single image in a matplotlib window.

    Args:
        image: Array to display.
        title: Window title.
        cmap: Matplotlib colourmap (ignored for colour images).
    """
    plt.imshow(image, cmap=cmap)
    plt.title(title)
    plt.axis("off")
    plt.show()


def display_multi_image(images: list[tuple]) -> None:
    """Show a grid of images in a single matplotlib figure.

    Each entry in images may be:
    - a bare array, or
    - a tuple of (array,) / (array, title) / (array, title, cmap).

    Args:
        images: List of image entries as described above.
    """
    if not images:
        return

    arrays, titles, cmaps = _unpack_image_entries(images)

    total = len(arrays)
    cols = min(3, total)
    rows = (total + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes_flat = np.array(axes).flatten() if not isinstance(axes, np.ndarray) else axes.flatten()

    for ax, image, title, cmap in zip(axes_flat, arrays, titles, cmaps):
        effective_cmap = cmap if cmap not in (None, "") else (
            "gray" if getattr(image, "ndim", 3) == 2 else None
        )
        ax.imshow(image, cmap=effective_cmap)
        ax.set_title(title)
        ax.axis("off")

    for ax in axes_flat[total:]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()


def select_pgm_file() -> FilePath:
    """Open a file-chooser dialog filtered to PGM files.

    Returns:
        Selected file path, or None if the user cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a PGM File",
        filetypes=[("PGM Files", "*.pgm"), ("All Files", "*.*")],
    )
    return file_path or None


def save_pgm_file() -> FilePath:
    """Open a save-file dialog that enforces the .pgm extension.

    Returns:
        Chosen save path, or None if the user cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save PGM File",
        defaultextension=".pgm",
        filetypes=[("PGM Files", "*.pgm")],
    )
    return file_path or None


def read_pgm_file(file_path: str | Path) -> ImageMatrix:
    """Parse a Plain PGM (P2) file and return its pixel data as an ImageMatrix.

    Only 8-bit ASCII PGM files (magic number P2) are supported.

    Args:
        file_path: Path to the .pgm file.

    Returns:
        2-D list of integer pixel values in [0, 255].

    Raises:
        ValueError: If the file format is not P2 or exceeds 8-bit range.
        FileNotFoundError: Propagated from open() if the file does not exist.
    """
    tokens = Path(file_path).read_text().split()

    if not tokens:
        raise ValueError("The PGM file is empty.")

    if tokens[0] != "P2":
        raise ValueError(f"Unsupported format '{tokens[0]}'. Only P2 (ASCII) is allowed.")

    width, height, max_value = int(tokens[1]), int(tokens[2]), int(tokens[3])

    if max_value > 255:
        raise ValueError("Only 8-bit images (max value ≤ 255) are supported.")

    pixel_tokens = tokens[4:]
    matrix: ImageMatrix = []
    index = 0

    for _ in range(height):
        row = []
        for c in range(width):
            row.append(int(pixel_tokens[index + c]))
        matrix.append(row)
        index += width

    return matrix


def write_pgm_file(file_path: str | Path, matrix: ImageMatrix) -> None:
    """Serialise an ImageMatrix to a Plain PGM (P2) file.

    Args:
        file_path: Destination path for the .pgm file.
        matrix: 2-D list of pixel values in [0, 255].
    """
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0

    row_strings = []
    for row in matrix:
        row_strings.append(" ".join(str(pixel) for pixel in row))

    content = f"P2\n{width} {height}\n255\n" + "\n".join(row_strings) + "\n"
    Path(file_path).write_text(content)


def image_matrix_to_numpy(matrix: ImageMatrix) -> np.ndarray:
    """Convert an ImageMatrix to a uint8 grayscale NumPy array.

    Args:
        matrix: 2-D list of pixel values in [0, 255].

    Returns:
        NumPy array of dtype uint8 with the same shape.
    """
    return np.array(matrix, dtype=np.uint8)


def numpy_to_image_matrix(array: np.ndarray) -> ImageMatrix:
    """Convert a NumPy array to an ImageMatrix.

    Colour (3-channel) arrays are converted to grayscale first.

    Args:
        array: Grayscale or BGR NumPy array.

    Returns:
        2-D list of integer pixel values.
    """
    if array.ndim == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    return array.tolist()


# --- Private helpers ---

def _unpack_image_entries(
    entries: list,
) -> tuple[list[np.ndarray], list[str], list[str | None]]:
    arrays, titles, cmaps = [], [], []

    for entry in entries:
        if isinstance(entry, tuple):
            image = entry[0]
            title = entry[1] if len(entry) > 1 else ""
            cmap = entry[2] if len(entry) > 2 else None
        else:
            image, title, cmap = entry, "", None

        arrays.append(image)
        titles.append(title)
        cmaps.append(cmap)

    return arrays, titles, cmaps
