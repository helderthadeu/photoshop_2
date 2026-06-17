"""Right-side inspector that edits the selected node's parameters generically.

The inspector never hard-codes UI per operation: it reads `block.parameters()`
and builds the matching widget for each `ParameterType`, seeding it from the
node's stored values and writing edits straight back onto `node.parameters`. A
re-selection rebuilds the form from scratch.
"""
from __future__ import annotations

from functools import partial
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.blocks.base import Parameter, ParameterType
from src.graph.node import Node
from src.gui import theme
from src.gui.widgets.matrix_editor import MatrixEditor
from src.gui.widgets.value_slider import SliderConfig, ValueSlider

_SPIN_FALLBACK_RANGE = 9999


class Inspector(QWidget):
    """Parameter editor bound to the currently selected node."""

    parameter_changed = Signal()
    path_browse_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._node: Node | None = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(8)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._title = QLabel("INSPECTOR")
        self._title.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
        self._layout.addWidget(self._title)

        self._body = QWidget()
        self._layout.addWidget(self._body)
        self.set_node(None)

    def set_node(self, node: Node | None) -> None:
        """Rebuild the form for `node`, or show a placeholder when None."""
        self._node = node
        self._replace_body()

        if node is None:
            self._show_placeholder()
            return
        self._show_node_form(node)

    # --- body construction --------------------------------------------------

    def _replace_body(self) -> None:
        self._layout.removeWidget(self._body)
        self._body.deleteLater()
        self._body = QWidget()
        self._layout.addWidget(self._body)

    def _show_placeholder(self) -> None:
        layout = QVBoxLayout(self._body)
        message = QLabel("Select a node to edit its parameters.")
        message.setStyleSheet(f"color: {theme.TEXT_DISABLED};")
        message.setWordWrap(True)
        layout.addWidget(message)

    def _show_node_form(self, node: Node) -> None:
        layout = QVBoxLayout(self._body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._node_header(node))

        parameters = node.block.parameters()
        if not parameters:
            hint = QLabel("This block has no parameters.")
            hint.setStyleSheet(f"color: {theme.TEXT_DISABLED};")
            layout.addWidget(hint)
            return

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        for parameter in parameters:
            form.addRow(parameter.label, self._build_widget(node, parameter))
        layout.addLayout(form)

    def _node_header(self, node: Node) -> QLabel:
        color = theme.category_color(node.block.category).name()
        header = QLabel(f"{node.block.display_name}\n{node.node_id}")
        header.setStyleSheet(
            f"color: {theme.TEXT}; font-size: 13px; font-weight: 600;"
            f" border-left: 3px solid {color}; padding-left: 8px;"
        )
        return header

    # --- per-type widgets ---------------------------------------------------

    def _build_widget(self, node: Node, parameter: Parameter) -> QWidget:
        value = node.parameters.get(parameter.name, parameter.default)
        builders = {
            ParameterType.INTEGER: self._build_integer,
            ParameterType.FLOAT: self._build_float,
            ParameterType.CHOICE: self._build_choice,
            ParameterType.TEXT: self._build_text,
            ParameterType.MATRIX: self._build_matrix,
        }
        builder = builders.get(parameter.parameter_type, self._build_text)
        return builder(node, parameter, value)

    def _build_integer(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        if not _is_ranged(parameter):
            return self._build_int_spinbox(node, parameter, value)
        config = SliderConfig(step=parameter.step, unit=parameter.unit, decimals=0)
        return self._build_slider(node, parameter, int(value), config)

    def _build_float(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        if not _is_ranged(parameter):
            return self._build_float_spinbox(node, parameter, value)
        config = SliderConfig(step=parameter.step, unit=parameter.unit,
                              decimals=_decimals_for(parameter.step))
        return self._build_slider(node, parameter, float(value), config)

    def _build_slider(
        self,
        node: Node,
        parameter: Parameter,
        value: float,
        config: SliderConfig,
    ) -> QWidget:
        slider = ValueSlider((parameter.minimum, parameter.maximum), value, config)
        slider.value_changed.connect(partial(self._store, node, parameter.name))
        return slider

    def _build_int_spinbox(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        spin = QSpinBox()
        spin.setRange(-_SPIN_FALLBACK_RANGE, _SPIN_FALLBACK_RANGE)
        spin.setValue(int(value))
        spin.valueChanged.connect(partial(self._store, node, parameter.name))
        return spin

    def _build_float_spinbox(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        spin = QDoubleSpinBox()
        spin.setDecimals(2)
        spin.setSingleStep(0.1)
        spin.setRange(-_SPIN_FALLBACK_RANGE, _SPIN_FALLBACK_RANGE)
        spin.setValue(float(value))
        spin.valueChanged.connect(partial(self._store, node, parameter.name))
        return spin

    def _build_choice(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        combo = QComboBox()
        combo.addItems(parameter.choice_labels or parameter.choices)
        if value in parameter.choices:
            combo.setCurrentIndex(parameter.choices.index(value))
        combo.currentIndexChanged.connect(partial(self._store_choice, node, parameter))
        return combo

    def _store_choice(self, node: Node, parameter: Parameter, index: int) -> None:
        self._store(node, parameter.name, parameter.choices[index])

    def _build_text(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        edit = QLineEdit(str(value))
        # Commit on Enter/focus-out, not per keystroke: a partial path must not
        # trigger execution (a Save sink would write a half-typed file name).
        edit.editingFinished.connect(partial(self._store_text, node, parameter.name, edit))
        if parameter.name != "path":
            return edit
        return self._with_browse_button(node, edit)

    def _with_browse_button(self, node: Node, edit: QLineEdit) -> QWidget:
        """Pair a path field with a button that asks the host to open a dialog."""
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        browse = QPushButton("Procurar…")
        browse.clicked.connect(partial(self.path_browse_requested.emit, node))
        row.addWidget(edit, 1)
        row.addWidget(browse)
        return container

    def _build_matrix(self, node: Node, parameter: Parameter, value: Any) -> QWidget:
        matrix = value if isinstance(value, list) else parameter.default
        editor = MatrixEditor(matrix)
        editor.matrix_changed.connect(partial(self._store, node, parameter.name))
        return editor

    def _store_text(self, node: Node, name: str, edit: QLineEdit) -> None:
        self._store(node, name, edit.text())

    def _store(self, node: Node, name: str, value: Any) -> None:
        node.parameters[name] = value
        self.parameter_changed.emit()


def _is_ranged(parameter: Parameter) -> bool:
    """True when both bounds are set, so a slider can span them."""
    return parameter.minimum is not None and parameter.maximum is not None


def _decimals_for(step: float) -> int:
    """Decimal places implied by a step (0.1 → 1, 1 → 0)."""
    text = str(step)
    if "." not in text:
        return 0
    fraction = text.split(".")[1].rstrip("0")
    return len(fraction) if fraction else 0
