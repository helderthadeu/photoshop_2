"""A small grid editor for square, odd-sized numeric matrices (e.g. kernels).

Renders one spin box per cell plus a size selector limited to odd sizes, so a
convolution kernel can be edited directly in the inspector. Emits the full matrix
whenever a cell or the size changes.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.gui import theme

Matrix = list[list[float]]

_ALLOWED_SIZES = [3, 5, 7, 9]
_CELL_LIMIT = 999.0


class MatrixEditor(QWidget):
    """Editable grid of numeric cells for an odd-sized square matrix."""

    matrix_changed = Signal(list)

    def __init__(self, matrix: Matrix) -> None:
        super().__init__()
        self._cells: list[list[QDoubleSpinBox]] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)
        outer.addLayout(self._build_size_row())

        self._grid_host = QWidget()
        self._grid = QGridLayout(self._grid_host)
        self._grid.setSpacing(4)
        outer.addWidget(self._grid_host)

        self.set_matrix(matrix)

    # --- public API ---------------------------------------------------------

    def matrix(self) -> Matrix:
        """Return the current matrix, using ints where the value is whole."""
        result: Matrix = []
        for row_cells in self._cells:
            row: list[float] = []
            for cell in row_cells:
                value = cell.value()
                row.append(int(value) if value == int(value) else value)
            result.append(row)
        return result

    def set_matrix(self, matrix: Matrix) -> None:
        """Populate the editor from `matrix`, falling back to a 3×3 if unusable."""
        size = len(matrix) if _is_square_odd(matrix) else _ALLOWED_SIZES[0]
        values = matrix if _is_square_odd(matrix) else _zeros(size)

        self._size_combo.blockSignals(True)
        self._size_combo.setCurrentText(_size_label(size))
        self._size_combo.blockSignals(False)
        self._rebuild_grid(values)

    # --- construction -------------------------------------------------------

    def _build_size_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        caption = QLabel("Tamanho")
        caption.setStyleSheet(f"color: {theme.TEXT_MUTED};")

        self._size_combo = QComboBox()
        for size in _ALLOWED_SIZES:
            self._size_combo.addItem(_size_label(size))
        self._size_combo.currentIndexChanged.connect(self._on_size_changed)

        row.addWidget(caption)
        row.addWidget(self._size_combo)
        row.addStretch(1)
        return row

    def _rebuild_grid(self, values: Matrix) -> None:
        self._clear_grid()
        self._cells = []
        for row_index, row_values in enumerate(values):
            cells: list[QDoubleSpinBox] = []
            for column_index, value in enumerate(row_values):
                cell = self._build_cell(value)
                self._grid.addWidget(cell, row_index, column_index)
                cells.append(cell)
            self._cells.append(cells)

    def _build_cell(self, value: float) -> QDoubleSpinBox:
        cell = QDoubleSpinBox()
        cell.setRange(-_CELL_LIMIT, _CELL_LIMIT)
        cell.setDecimals(2)
        cell.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        cell.setFixedWidth(54)
        cell.setValue(float(value))
        cell.valueChanged.connect(self._emit_matrix)
        return cell

    def _clear_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # --- reactions ----------------------------------------------------------

    def _on_size_changed(self) -> None:
        size = _ALLOWED_SIZES[self._size_combo.currentIndex()]
        self._rebuild_grid(_resized(self.matrix(), size))
        self._emit_matrix()

    def _emit_matrix(self) -> None:
        self.matrix_changed.emit(self.matrix())


def _size_label(size: int) -> str:
    return f"{size} × {size}"


def _is_square_odd(matrix: Matrix) -> bool:
    if not matrix or len(matrix) % 2 == 0:
        return False
    for row in matrix:
        if len(row) != len(matrix):
            return False
    return True


def _zeros(size: int) -> Matrix:
    grid: Matrix = []
    for _ in range(size):
        grid.append([0] * size)
    return grid


def _resized(matrix: Matrix, size: int) -> Matrix:
    """Resize to `size`×`size`, keeping overlapping values and zero-filling."""
    resized = _zeros(size)
    for row_index in range(min(size, len(matrix))):
        for column_index in range(min(size, len(matrix[row_index]))):
            resized[row_index][column_index] = matrix[row_index][column_index]
    return resized
