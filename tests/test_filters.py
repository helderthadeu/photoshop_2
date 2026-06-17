"""Tests for the spatial filters, guarding the Gaussian and median regressions."""
import math

import pytest

from src.domain.filters import (
    _build_gaussian_kernel,
    apply_average_filter,
    apply_derivative_filter,
    apply_gaussian_filter,
    apply_laplacian_filter,
    apply_median_filter,
)


def test_gaussian_kernel_sums_to_one():
    kernel = _build_gaussian_kernel(5)
    total = sum(value for row in kernel for value in row)
    assert math.isclose(total, 1.0, abs_tol=1e-9)


def test_gaussian_centre_is_the_maximum_weight():
    kernel = _build_gaussian_kernel(5)
    weights = [value for row in kernel for value in row]
    assert kernel[2][2] == max(weights)


def test_gaussian_preserves_a_uniform_region():
    image = [[120] * 7 for _ in range(7)]
    assert int(apply_gaussian_filter(image, 3)[3][3]) == 120


def test_average_preserves_a_uniform_region():
    image = [[80] * 7 for _ in range(7)]
    assert int(apply_average_filter(image, 3)[3][3]) == 80


def test_median_returns_the_true_median():
    window = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
    assert int(apply_median_filter(window, 3)[1][1]) == 50


def test_laplacian_of_a_flat_region_is_zero():
    image = [[100] * 5 for _ in range(5)]
    assert int(apply_laplacian_filter(image, 3, 1.0)[2][2]) == 0


def test_even_kernel_size_raises():
    with pytest.raises(ValueError):
        apply_median_filter([[1, 2], [3, 4]], 2)


def test_derivative_invalid_direction_raises():
    with pytest.raises(ValueError):
        apply_derivative_filter([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 3, "z")
