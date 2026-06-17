"""Tests for the convolution engine: padding, clamping, and validation."""
import numpy as np
import pytest

from src.domain.convolution import apply_convolution, pad_image


def test_pad_image_defaults_to_zero_border():
    padded = pad_image([[5]], 1)
    assert padded[0][0] == 0  # border is black, not white
    assert padded[1][1] == 5  # the original pixel stays centred


def test_identity_kernel_preserves_image():
    image = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
    identity = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert apply_convolution(image, identity).tolist() == image


def test_negative_response_clamps_to_zero():
    image = [[100, 100, 100], [100, 100, 100], [100, 100, 100]]
    assert int(apply_convolution(image, [[-1]])[1][1]) == 0


def test_large_response_clamps_to_255():
    image = [[100, 100, 100], [100, 100, 100], [100, 100, 100]]
    assert int(apply_convolution(image, [[3]])[1][1]) == 255


def test_result_dtype_is_uint8():
    assert apply_convolution([[1, 2, 3]], [[1]]).dtype == np.uint8


def test_even_kernel_raises():
    with pytest.raises(ValueError):
        apply_convolution([[1, 2], [3, 4]], [[1, 1], [1, 1]])


def test_kernel_larger_than_image_raises():
    with pytest.raises(ValueError):
        apply_convolution([[1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]])
