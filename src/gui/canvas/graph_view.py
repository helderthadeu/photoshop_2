"""The canvas viewport: dotted grid, wheel zoom, middle-button pan, block drops.

`GraphView` renders a `GraphScene` with a Fusion-style dotted backdrop and the
navigation expected of a node editor. It also receives blocks dragged from the
library: a drop resolves the block class from `BLOCK_REGISTRY` and asks the scene
to place a node at the cursor.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsView

from src.blocks.base import BLOCK_REGISTRY
from src.gui import theme
from src.gui.canvas.graph_scene import GraphScene
from src.gui.dialogs.block_setup import initial_parameters
from src.gui.drag_mime import BLOCK_MIME_TYPE

_GRID_SPACING = 26
_ZOOM_STEP = 1.15
_MIN_SCALE = 0.4
_MAX_SCALE = 2.5


class GraphView(QGraphicsView):
    """Pan/zoom viewport over a node graph that accepts library drops."""

    def __init__(self, scene: GraphScene) -> None:
        super().__init__(scene)
        self._scene = scene
        self._scale = 1.0
        self._pan_origin: QPointF | None = None

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setAcceptDrops(True)

    # --- background ---------------------------------------------------------

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # standards: allow-framework-override
        painter.fillRect(rect, QColor(theme.BACKGROUND))
        self._draw_grid_dots(painter, rect)

    def _draw_grid_dots(self, painter: QPainter, rect: QRectF) -> None:
        painter.setPen(QColor(theme.BORDER))
        left = int(rect.left()) - (int(rect.left()) % _GRID_SPACING)
        top = int(rect.top()) - (int(rect.top()) % _GRID_SPACING)

        y = top
        while y < rect.bottom():
            x = left
            while x < rect.right():
                painter.drawPoint(x, y)
                x += _GRID_SPACING
            y += _GRID_SPACING

    # --- zoom ---------------------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:  # standards: allow-framework-override
        zoom_in = event.angleDelta().y() > 0
        factor = _ZOOM_STEP if zoom_in else 1.0 / _ZOOM_STEP
        self._apply_zoom(factor)

    def _apply_zoom(self, factor: float) -> None:
        target = self._scale * factor
        if target < _MIN_SCALE or target > _MAX_SCALE:
            return
        self._scale = target
        self.scale(factor, factor)

    # --- pan (middle button) -----------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:  # standards: allow-framework-override
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_origin = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # standards: allow-framework-override
        if self._pan_origin is not None:
            self._pan_by(event.position())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # standards: allow-framework-override
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_origin is not None:
            self._pan_origin = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _pan_by(self, position: QPointF) -> None:
        delta = position - self._pan_origin
        self._pan_origin = position
        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta.x()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta.y()))

    # --- drag-and-drop from the block library ------------------------------

    def dragEnterEvent(self, event) -> None:  # standards: allow-framework-override
        if event.mimeData().hasFormat(BLOCK_MIME_TYPE):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:  # standards: allow-framework-override
        if event.mimeData().hasFormat(BLOCK_MIME_TYPE):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # standards: allow-framework-override
        class_name = bytes(event.mimeData().data(BLOCK_MIME_TYPE)).decode("utf-8")
        block_class = BLOCK_REGISTRY.get(class_name)
        if block_class is None:
            return

        parameters = initial_parameters(block_class, self)
        if parameters is None:  # the user cancelled a required setup dialog
            return

        scene_pos = self.mapToScene(event.position().toPoint())
        self._scene.add_block_node(block_class, scene_pos, parameters)
        event.acceptProposedAction()
