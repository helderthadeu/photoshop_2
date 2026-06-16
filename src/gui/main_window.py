"""The main editor window: block palette, node canvas placeholder, run action.

This is an intentionally minimal shell. Node graphics, connection drawing, and
parameter panels are added on top of the canvas/ and panels/ subpackages.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QGraphicsScene,
    QGraphicsView,
    QListWidget,
    QMainWindow,
)

from src.blocks.base import BLOCK_REGISTRY
import src.blocks  # noqa: F401  (imported to populate BLOCK_REGISTRY)


class MainWindow(QMainWindow):
    """Top-level window hosting the node canvas and the block palette."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PSE-Image")
        self.resize(1200, 800)

        self._scene = QGraphicsScene(self)
        self._canvas = QGraphicsView(self._scene, self)
        self.setCentralWidget(self._canvas)

        self._build_block_palette()

    def _build_block_palette(self) -> None:
        """Populate a dock listing every registered block, grouped by category."""
        palette = QListWidget(self)

        for block_class in BLOCK_REGISTRY.values():
            instance = block_class()
            palette.addItem(f"{instance.category} — {instance.display_name}")

        dock = QDockWidget("Blocks", self)
        dock.setWidget(palette)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
