"""Tests for the PGM codec and the any-image→PGM conversion."""
import cv2
import numpy as np
import pytest

from src.infrastructure.image_loader import ensure_pgm
from src.infrastructure.pgm_codec import read_pgm_file, read_pgm_header, write_pgm_file


def test_pgm_round_trip(tmp_path):
    matrix = [[0, 50, 100], [150, 200, 255]]
    path = tmp_path / "img.pgm"
    write_pgm_file(path, matrix)
    assert read_pgm_file(path) == matrix


def test_pgm_header(tmp_path):
    path = tmp_path / "img.pgm"
    write_pgm_file(path, [[1, 2, 3], [4, 5, 6]])
    assert read_pgm_header(path) == (3, 2, 255)


def test_pgm_rejects_non_p2(tmp_path):
    path = tmp_path / "bad.pgm"
    path.write_text("P5 2 2 255 1 2 3 4")
    with pytest.raises(ValueError):
        read_pgm_file(path)


def test_pgm_rejects_over_8bit(tmp_path):
    path = tmp_path / "big.pgm"
    path.write_text("P2 1 1 65535 100")
    with pytest.raises(ValueError):
        read_pgm_file(path)


def test_ensure_pgm_passes_through_existing_pgm(tmp_path):
    path = tmp_path / "x.pgm"
    write_pgm_file(path, [[1, 2], [3, 4]])
    assert ensure_pgm(path) == path


def test_ensure_pgm_converts_other_formats(tmp_path):
    png = tmp_path / "x.png"
    cv2.imwrite(str(png), np.zeros((4, 6, 3), dtype=np.uint8))
    converted = ensure_pgm(png)
    assert converted.suffix == ".pgm"
    assert read_pgm_header(converted) == (6, 4, 255)
