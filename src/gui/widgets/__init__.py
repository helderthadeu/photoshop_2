"""Reusable low-level Qt widgets shared across panels and the canvas."""
from src.gui.widgets.matrix_editor import MatrixEditor
from src.gui.widgets.topbar import TopBar
from src.gui.widgets.value_slider import SliderConfig, ValueSlider

__all__ = ["MatrixEditor", "SliderConfig", "TopBar", "ValueSlider"]
