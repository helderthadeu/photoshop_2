"""Hand-written Plain PGM (P2) reader and writer — no ready-made codecs."""
from pathlib import Path

from src.domain.types import ImageMatrix


def read_pgm_file(file_path: str | Path) -> ImageMatrix:
    """Parse a Plain PGM (P2) file and return its pixel data as an ImageMatrix.

    Only 8-bit ASCII PGM files (magic number P2) are supported.

    Args:
        file_path: Path to the .pgm file.

    Returns:
        2-D list of integer pixel values in [0, 255].

    Raises:
        ValueError: If the file format is not P2 or exceeds 8-bit range.
        FileNotFoundError: If the file does not exist.
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
