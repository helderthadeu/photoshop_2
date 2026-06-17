"""Convert any supported image to a cached grayscale PGM. cv2 is confined here."""
import hashlib
import tempfile
from pathlib import Path

import cv2

from src.domain.types import ImageMatrix
from src.infrastructure.pgm_codec import write_pgm_file


def ensure_pgm(source_path: str | Path) -> Path:
    """Return a PGM path for `source_path`, converting other formats first.

    A `.pgm` source is returned unchanged. Any other format OpenCV can read is
    loaded as 8-bit grayscale and written as a PGM into a cache directory, so the
    rest of the pipeline always works on a real PGM file.

    Args:
        source_path: Path to a PGM or any OpenCV-readable image.

    Returns:
        Path to the PGM version of the image.

    Raises:
        FileNotFoundError: If OpenCV cannot read the source image.
    """
    source = Path(source_path)
    if source.suffix.lower() == ".pgm":
        return source

    matrix = _load_grayscale_matrix(source)
    target = _converted_pgm_path(source)
    write_pgm_file(target, matrix)
    return target


def _load_grayscale_matrix(source: Path) -> ImageMatrix:
    """Load any OpenCV-readable image as an 8-bit grayscale ImageMatrix."""
    image = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Unsupported or missing image: {source}")
    return image.tolist()


def _converted_pgm_path(source: Path) -> Path:
    """A deterministic cache path for the PGM converted from `source`."""
    cache_dir = Path(tempfile.gettempdir()) / "pse_image_pgm"
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(str(source.resolve()).encode("utf-8")).hexdigest()[:8]
    return cache_dir / f"{source.stem}_{digest}.pgm"
