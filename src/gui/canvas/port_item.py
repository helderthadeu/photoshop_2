"""Graphics item for a single input/output socket on a node.

A `PortItem` is a child of its `NodeItem`, drawn as a small circle on the left
(inputs) or right (outputs) edge. It carries the identity needed to build a
graph `Connection` (owning node id + port name) and keeps back-references to the
connection items touching it so they can redraw when the node moves.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem

from src.blocks.base import PortDirection
from src.gui import theme

if TYPE_CHECKING:
    from src.gui.canvas.connection_item import ConnectionItem

PORT_RADIUS = 6.0


class PortItem(QGraphicsItem):
    """A socket on a node edge that anchors connections."""

    def __init__(
        self,
        node_id: str,
        port_name: str,
        direction: PortDirection,
        color: QColor,
        parent: QGraphicsItem,
    ) -> None:
        super().__init__(parent)
        self.node_id = node_id
        self.port_name = port_name
        self.direction = direction
        self._color = color
        self.connections: list[ConnectionItem] = []
        self.setAcceptHoverEvents(True)
        self.setToolTip(port_name)

    def is_input(self) -> bool:
        """True when this socket consumes an upstream value."""
        return self.direction == PortDirection.INPUT

    def scene_center(self) -> QPointF:
        """Return the socket centre in scene coordinates for path drawing."""
        return self.mapToScene(QPointF(0.0, 0.0))

    def boundingRect(self) -> QRectF:  # standards: allow-framework-override
        margin = 2.0
        span = PORT_RADIUS + margin
        return QRectF(-span, -span, span * 2, span * 2)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # standards: allow-framework-override
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        fill = self._color if self.connections else QColor(theme.BACKGROUND_ALT)
        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(self._color, 1.5))
        painter.drawEllipse(QPointF(0.0, 0.0), PORT_RADIUS, PORT_RADIUS)

    def hoverEnterEvent(self, event) -> None:  # standards: allow-framework-override
        self.setCursor(Qt.CursorShape.CrossCursor)
        super().hoverEnterEvent(event)
