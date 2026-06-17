"""Bottom console that logs execution progress and connection errors.

A thin wrapper over a read-only text view offering levelled, colour-coded
messages (info/success/warning/error) in a monospaced font, mirroring the
execution feedback area of a node compositor.
"""
from __future__ import annotations

from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from src.gui import theme

_LEVEL_COLORS = {
    "info": theme.TEXT_MUTED,
    "success": theme.SUCCESS,
    "warning": theme.WARNING,
    "error": theme.ERROR,
}


class Console(QPlainTextEdit):
    """A read-only, colourised execution log."""

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont(theme.MONO_FONT_FAMILY, 10))
        self.setMaximumBlockCount(500)
        self.info("PSE-Image Studio ready.")

    def info(self, message: str) -> None:
        """Log a neutral status message."""
        self._append("info", message)

    def success(self, message: str) -> None:
        """Log a successful outcome."""
        self._append("success", message)

    def warning(self, message: str) -> None:
        """Log a non-fatal warning."""
        self._append("warning", message)

    def error(self, message: str) -> None:
        """Log a failure."""
        self._append("error", message)

    def _append(self, level: str, message: str) -> None:
        color = _LEVEL_COLORS.get(level, theme.TEXT)
        stamp = datetime.now().strftime("%H:%M:%S")
        line = (
            f'<span style="color:{theme.TEXT_DISABLED}">[{stamp}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        self.appendHtml(line)
