"""Tests for point operations, guarding against uint8 overflow from upstream blocks."""
import numpy as np

from src.domain.point import adjust_brightness, apply_threshold


def test_brightness_clamps_to_white_without_uint8_wraparound():
    # A uint8 array is what an upstream filter (e.g. Average) feeds in. A +255
    # bias must saturate to 255, not wrap around to a near-identical image.
    image = np.array([[10, 20], [30, 200]], dtype=np.uint8)
    assert adjust_brightness(image, 255) == [[255, 255], [255, 255]]


def test_brightness_accepts_negative_bias_on_uint8_input():
    image = np.array([[10, 200]], dtype=np.uint8)
    assert adjust_brightness(image, -3) == [[7, 197]]


def test_brightness_clamps_to_black_on_large_negative_bias():
    image = np.array([[10, 200]], dtype=np.uint8)
    assert adjust_brightness(image, -255) == [[0, 0]]


def test_brightness_still_handles_plain_matrix():
    assert adjust_brightness([[10, 20], [30, 200]], 102) == [[112, 122], [132, 255]]


def test_threshold_handles_uint8_input():
    image = np.array([[100, 128], [200, 50]], dtype=np.uint8)
    assert apply_threshold(image, 128) == [[0, 255], [255, 0]]
