"""Shared presentational building blocks for the file dialogs.

The Load and Save dialogs share the same visual language — a heading, captioned
sections, and bordered cards. These helpers keep that look in one place so both
dialogs stay identical without duplicating layout code.
"""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QLayout, QVBoxLayout, QWidget

from src.gui import theme


def dialog_title(text: str) -> QLabel:
    """The bold heading shown at the top of a dialog."""
    label = QLabel(text)
    label.setStyleSheet(f"color: {theme.TEXT}; font-size: 15px; font-weight: 600;")
    return label


def titled_section(title: str, body: QWidget) -> QWidget:
    """A muted uppercase caption stacked above a body widget."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    caption = QLabel(title)
    caption.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
    layout.addWidget(caption)
    layout.addWidget(body)
    return container


def framed(inner: QLayout) -> QFrame:
    """Wrap a layout in the standard raised, bordered card."""
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background-color: {theme.PANEL_RAISED};"
        f" border: 1px solid {theme.BORDER}; border-radius: 6px; }}"
    )
    inner.setContentsMargins(12, 10, 12, 10)
    frame.setLayout(inner)
    return frame
