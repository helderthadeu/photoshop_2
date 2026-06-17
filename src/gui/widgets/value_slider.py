"""A labelled slider for a bounded numeric parameter.

Wraps a QSlider with a value readout and snaps to a fixed step, so it can drive
integers (brightness %, threshold), odd-only kernel sizes (step 2), or floats
(sigma). The slider works in integer "ticks" internally and maps them back to the
real value range, emitting the resolved value on every change.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

from src.gui import theme


class ValueSlider(QWidget):
    """A horizontal slider plus a readout, snapping to a step and showing a unit."""

    value_changed = Signal(object)

    def __init__(
        self,
        bounds: tuple[float, float],
        value: float,
        config: "SliderConfig",
    ) -> None:
        super().__init__()
        self._minimum, maximum = bounds
        self._step = config.step
        self._unit = config.unit
        self._decimals = config.decimals
        self._ticks = max(1, round((maximum - self._minimum) / self._step))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, self._ticks)
        self._slider.setValue(self._tick_for(value))
        self._slider.valueChanged.connect(self._on_slider)

        self._readout = QLabel()
        self._readout.setMinimumWidth(48)
        self._readout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._readout.setStyleSheet(f"color: {theme.TEXT}; font-weight: 600;")

        layout.addWidget(self._slider, 1)
        layout.addWidget(self._readout)
        self._update_readout(self.value())

    def value(self) -> float | int:
        """Return the current resolved value (int when `decimals` is 0)."""
        return self._value_for(self._slider.value())

    def _value_for(self, tick: int) -> float | int:
        raw = self._minimum + tick * self._step
        if self._decimals == 0:
            return int(round(raw))
        return round(raw, self._decimals)

    def _tick_for(self, value: float) -> int:
        tick = round((value - self._minimum) / self._step)
        return max(0, min(self._ticks, tick))

    def _on_slider(self, tick: int) -> None:
        value = self._value_for(tick)
        self._update_readout(value)
        self.value_changed.emit(value)

    def _update_readout(self, value: float | int) -> None:
        if self._decimals == 0:
            self._readout.setText(f"{value}{self._unit}")
        else:
            self._readout.setText(f"{value:.{self._decimals}f}{self._unit}")


class SliderConfig:
    """Presentation settings for a `ValueSlider` (step, unit, decimal places)."""

    def __init__(self, step: float = 1, unit: str = "", decimals: int = 0) -> None:
        self.step = step
        self.unit = unit
        self.decimals = decimals
