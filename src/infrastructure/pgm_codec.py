"""Hand-written Plain PGM (P2) writer and cv2-based reader for format flexibility."""
from pathlib import Path

import cv2

from src.domain.types import ImageMatrix


def read_pgm_file(file_path: str | Path) -> ImageMatrix:
    """Parse a PGM file and return its pixel data as an ImageMatrix.

    Supports both ASCII (P2) and binary (P5) PGM formats, 8-bit only.
    Uses OpenCV for robust reading of both formats.

    Args:
        file_path: Path to the .pgm file.

    Returns:
        2-D list of integer pixel values in [0, 255].

    Raises:
        ValueError: If the file format is not PGM or exceeds 8-bit range.
        FileNotFoundError: If the file does not exist.
    """
    source = Path(file_path)
    
    # Use cv2 to handle both P2 (ASCII) and P5 (binary) formats
    image = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Cannot read PGM file: {source}")
    
    # Convert numpy array to list of lists
    matrix = image.tolist()
    
    # Verify 8-bit range
    max_val = max(max(row) for row in matrix) if matrix else 0
    if max_val > 255:
        raise ValueError(f"Only 8-bit images (max value ≤ 255) are supported, got {max_val}.")
    
    return matrix


def read_pgm_header(file_path: str | Path) -> tuple[int, int, int]:
    """Return the (width, height, max_value) declared in a PGM header.

    Supports both ASCII (P2) and binary (P5) PGM formats.

    Args:
        file_path: Path to the .pgm file.

    Returns:
        A tuple of width, height, and the maximum intensity value.

    Raises:
        ValueError: If the file is not a valid PGM or its header is incomplete.
        FileNotFoundError: If the file does not exist.
    """
    source = Path(file_path)
    
    # Read header manually to avoid loading entire file
    with open(source, 'rb') as f:
        # Read first line (magic number)
        magic = f.readline().decode('ascii').strip()
        if magic not in ('P2', 'P5'):
            raise ValueError(f"Unsupported format '{magic}'. Only P2 (ASCII) and P5 (binary) are allowed.")
        
        # Skip comments
        while True:
            line = f.readline().decode('ascii').strip()
            if line and not line.startswith('#'):
                break
        
        # Parse width height
        w, h = map(int, line.split())
        
        # Skip comments and read max value
        while True:
            line = f.readline().decode('ascii').strip()
            if line and not line.startswith('#'):
                break
        
        max_val = int(line)
    
    return w, h, max_val


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
