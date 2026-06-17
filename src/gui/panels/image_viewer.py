"""A viewer that renders a grayscale image (ImageMatrix or NumPy) as a pixmap.

The viewer clamps any incoming intensities to the 0–255 byte range — filter
outputs can exceed it — and shows the result scaled to fit while preserving
aspect ratio. It is deliberately display-only; no processing happens here.
"""
from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.domain.types import ImageMatrix
from src.gui import theme


class ImageViewer(QWidget):
    """Display panel for a single grayscale image."""

    def __init__(self, title: str = "VIEWER") -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None
        self._role = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._title = QLabel(title)
        self._title.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
        layout.addWidget(self._title)

        self._canvas = QLabel("No image")
        self._canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._canvas.setStyleSheet(
            f"background-color: {theme.BACKGROUND}; color: {theme.TEXT_DISABLED};"
            f" border: 1px solid {theme.BORDER}; border-radius: 4px;"
        )
        # Expanding fills the panel so the image is shown large; the explicit
        # 1×1 minimum overrides the QLabel's pixmap-based minimum, which is what
        # otherwise fed back on every resize and grew the viewer without bound.
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._canvas.setMinimumSize(1, 1)
        layout.addWidget(self._canvas)

    def show_image(self, image: ImageMatrix | np.ndarray, subtitle: str | None = None) -> None:
        """Render `image`, optionally updating the panel subtitle."""
        self._pixmap = QPixmap.fromImage(to_grayscale_qimage(image))
        if subtitle is not None:
            self._title.setText(subtitle)
        self._rescale()

    def clear_image(self) -> None:
        """Reset the panel to its empty state and restore the role label."""
        self._pixmap = None
        self._canvas.setText("No image")
        self._title.setText(self._role)

    def resizeEvent(self, event) -> None:  # standards: allow-framework-override
        self._rescale()
        super().resizeEvent(event)

    def _rescale(self) -> None:
        if self._pixmap is None:
            return
        scaled = self._pixmap.scaled(
            self._canvas.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._canvas.setPixmap(scaled)


def first_image(port_values: dict[str, object]) -> ImageMatrix | np.ndarray | None:
    """Return the first port value that is a 2D grayscale image, else None.

    Used by the live preview to pick a displayable image out of a node's input
    or output mapping without knowing the port names in advance.
    """
    for value in port_values.values():
        if _is_displayable_image(value):
            return value
    return None


def _is_displayable_image(value: object) -> bool:
    if isinstance(value, np.ndarray):
        return value.ndim == 2
    return isinstance(value, list) and bool(value) and isinstance(value[0], list)


def to_grayscale_qimage(image: ImageMatrix | np.ndarray) -> QImage:
    """Clamp to bytes and wrap the pixels in an 8-bit grayscale QImage."""
    array = np.asarray(image)
    clamped = np.clip(array, 0, 255).astype(np.uint8)
    if clamped.ndim != 2:
        raise ValueError("ImageViewer expects a 2D grayscale image.")

    height, width = clamped.shape
    contiguous = np.ascontiguousarray(clamped)
    qimage = QImage(contiguous.data, width, height, width, QImage.Format.Format_Grayscale8)
    # copy() detaches the QImage from the temporary numpy buffer.
    return qimage.copy()
