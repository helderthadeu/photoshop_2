"""Graphics item for a bezier link between two ports.

A `ConnectionItem` draws a horizontal cubic curve from a source (output) port to
a target (input) port. While the user is dragging a new link, the target may be
absent and a free scene point is used as the endpoint instead. Once committed, a
link is selectable so it can be deleted (a widened hit area makes the thin curve
easy to click; selection tints it red).
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPainterPathStroker, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyle

from src.gui import theme
from src.gui.canvas.port_item import PortItem

_CONTROL_MIN_OFFSET = 60.0
_HIT_WIDTH = 12.0


class ConnectionItem(QGraphicsPathItem):
    """A bezier edge anchored to a source port and (optionally) a target port."""

    def __init__(self, source_port: PortItem) -> None:
        super().__init__()
        self.source_port = source_port
        self.target_port: PortItem | None = None
        self._free_end = source_port.scene_center()
        self._base_color = QColor(theme.TEXT_MUTED)

        self.setZValue(-1.0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self._apply_pen(self._base_color)
        self.update_path()

    def attach_target(self, target_port: PortItem) -> None:
        """Bind the loose end to a real input port and recolour the link."""
        self.target_port = target_port
        self._base_color = QColor(theme.ACCENT)
        self._apply_pen(self._base_color)
        self.update_path()

    def set_free_end(self, scene_point: QPointF) -> None:
        """Move the loose endpoint to follow the cursor during a drag."""
        self._free_end = scene_point
        self.update_path()

    def update_path(self) -> None:
        """Recompute the cubic path from current endpoint positions."""
        start = self.source_port.scene_center()
        end = self.target_port.scene_center() if self.target_port else self._free_end
        self.setPath(_horizontal_bezier(start, end))

    # --- interaction geometry ----------------------------------------------

    def shape(self) -> QPainterPath:  # standards: allow-framework-override
        stroker = QPainterPathStroker()
        stroker.setWidth(_HIT_WIDTH)
        return stroker.createStroke(self.path())

    def boundingRect(self) -> QRectF:  # standards: allow-framework-override
        return self.shape().boundingRect()

    def paint(self, painter, option, widget=None) -> None:  # standards: allow-framework-override
        # Drop the default dashed selection box; show selection via colour instead.
        option.state &= ~QStyle.StateFlag.State_Selected
        if self.isSelected():
            self.setPen(QPen(QColor(theme.ERROR), 2.5))
        else:
            self.setPen(QPen(self._base_color, 2.0))
        super().paint(painter, option, widget)

    def hoverEnterEvent(self, event) -> None:  # standards: allow-framework-override
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().hoverEnterEvent(event)

    def _apply_pen(self, color: QColor) -> None:
        self.setPen(QPen(color, 2.0))


def _horizontal_bezier(start: QPointF, end: QPointF) -> QPainterPath:
    """Build a left-to-right cubic curve with horizontal control tangents."""
    offset = max(_CONTROL_MIN_OFFSET, abs(end.x() - start.x()) * 0.5)
    control_one = QPointF(start.x() + offset, start.y())
    control_two = QPointF(end.x() - offset, end.y())

    path = QPainterPath(start)
    path.cubicTo(control_one, control_two, end)
    return path
