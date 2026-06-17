"""Modal dialog that plots a node's intensity histogram as a bar chart.

Opened by double-clicking a Histogram block. Shows the 256 intensity counts as
bars plus a couple of summary statistics. Purely a viewer — saving a histogram to
disk is done by wiring the Histogram block into a Save PGM sink.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.gui import theme
from src.gui.dialogs.layout_helpers import dialog_title, framed, titled_section


class HistogramDialog(QDialog):
    """A read-only histogram plot with summary statistics."""

    def __init__(self, histogram: list[int], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Histograma")
        self.setModal(True)
        self.setMinimumSize(480, 360)
        self._histogram = histogram

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        layout.addWidget(dialog_title("Histograma"))
        layout.addWidget(self._chart_section(), 1)
        layout.addWidget(self._info_section())
        layout.addLayout(self._button_row())

    def _chart_section(self) -> QWidget:
        chart = _HistogramChart(self._histogram)
        return titled_section("DISTRIBUIÇÃO DE INTENSIDADES", chart)

    def _info_section(self) -> QWidget:
        total = sum(self._histogram)
        peak_count = max(self._histogram) if self._histogram else 0
        peak_level = self._histogram.index(peak_count) if peak_count else 0

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)
        cells = [
            (0, 0, "Total de pixels:", f"{total}"),
            (0, 2, "Pico:", f"{peak_count} px"),
            (1, 0, "Intensidade do pico:", f"{peak_level}"),
        ]
        for row, column, caption, value in cells:
            caption_label = QLabel(caption)
            caption_label.setStyleSheet(f"color: {theme.TEXT_MUTED};")
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {theme.TEXT}; font-weight: 600;")
            grid.addWidget(caption_label, row, column)
            grid.addWidget(value_label, row, column + 1)

        return titled_section("INFORMAÇÕES", framed(grid))

    def _button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch(1)
        close_button = QPushButton("Fechar")
        close_button.setProperty("accent", "true")
        close_button.clicked.connect(self.accept)
        row.addWidget(close_button)
        return row


class _HistogramChart(QWidget):
    """Draws 256 intensity counts as accent-coloured bars on a dark backdrop."""

    def __init__(self, histogram: list[int]) -> None:
        super().__init__()
        self._histogram = histogram
        self.setMinimumHeight(180)

    def paintEvent(self, event) -> None:  # standards: allow-framework-override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect()
        painter.fillRect(area, QColor(theme.BACKGROUND))
        painter.setPen(QColor(theme.BORDER))
        painter.drawRect(area.adjusted(0, 0, -1, -1))

        peak = max(self._histogram) if self._histogram else 0
        if peak == 0:
            return
        self._paint_bars(painter, area, peak)

    def _paint_bars(self, painter: QPainter, area, peak: int) -> None:
        bins = len(self._histogram)
        usable_height = area.height() - 2
        bar_width = area.width() / bins

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.ACCENT))
        for index, count in enumerate(self._histogram):
            bar_height = count / peak * usable_height
            left = area.left() + index * bar_width
            top = area.bottom() - bar_height
            painter.drawRect(QRectF(left, top, bar_width + 0.5, bar_height))
