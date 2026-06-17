"""Graphics item representing one placed block on the canvas.

A `NodeItem` renders a rounded card with a category-coloured header, the block's
display name, and its input/output sockets. It wraps a graph `Node`, keeps that
node's stored position in sync as the user drags, and triggers connected links to
redraw on every move.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem

from src.graph.node import Node
from src.gui import theme
from src.gui.canvas.port_item import PORT_RADIUS, PortItem

NODE_WIDTH = 170.0
_HEADER_HEIGHT = 26.0
_ROW_HEIGHT = 22.0
_BODY_TOP_PADDING = 8.0
_BODY_BOTTOM_PADDING = 10.0
_CORNER_RADIUS = 6.0
_LABEL_MARGIN = 10.0


class NodeItem(QGraphicsItem):
    """A draggable card bound to a graph node and its block's ports."""

    def __init__(self, node: Node) -> None:
        super().__init__()
        self.node = node
        self._color = theme.category_color(node.block.category)
        self._height = self._compute_height()
        self.input_ports: list[PortItem] = []
        self.output_ports: list[PortItem] = []

        self._configure_flags()
        self._build_ports()
        self.setPos(QPointF(node.position[0], node.position[1]))

    # --- geometry -----------------------------------------------------------

    def boundingRect(self) -> QRectF:  # standards: allow-framework-override
        return QRectF(-PORT_RADIUS, 0.0, NODE_WIDTH + PORT_RADIUS * 2, self._height)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # standards: allow-framework-override
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_body(painter)
        self._paint_header(painter)
        self._paint_port_labels(painter)
        if self.isSelected():
            self._paint_selection(painter)

    def itemChange(self, change, value):  # standards: allow-framework-override
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._sync_position()
            self._redraw_connections()
        return super().itemChange(change, value)

    # --- construction helpers ----------------------------------------------

    def _configure_flags(self) -> None:
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def _build_ports(self) -> None:
        for index, port in enumerate(self.node.block.input_ports()):
            item = PortItem(self.node.node_id, port.name, port.direction, self._color, self)
            item.setPos(QPointF(0.0, self._row_y(index)))
            self.input_ports.append(item)

        for index, port in enumerate(self.node.block.output_ports()):
            item = PortItem(self.node.node_id, port.name, port.direction, self._color, self)
            item.setPos(QPointF(NODE_WIDTH, self._row_y(index)))
            self.output_ports.append(item)

    def _compute_height(self) -> float:
        input_count = len(self.node.block.input_ports())
        output_count = len(self.node.block.output_ports())
        rows = max(input_count, output_count, 1)
        body = _BODY_TOP_PADDING + rows * _ROW_HEIGHT + _BODY_BOTTOM_PADDING
        return _HEADER_HEIGHT + body

    def _row_y(self, index: int) -> float:
        return _HEADER_HEIGHT + _BODY_TOP_PADDING + index * _ROW_HEIGHT + _ROW_HEIGHT / 2

    # --- painting helpers ---------------------------------------------------

    def _paint_body(self, painter: QPainter) -> None:
        body_rect = QRectF(0.0, 0.0, NODE_WIDTH, self._height)
        painter.setBrush(QBrush(QColor(theme.PANEL_RAISED)))
        painter.setPen(QPen(QColor(theme.BORDER), 1.0))
        painter.drawRoundedRect(body_rect, _CORNER_RADIUS, _CORNER_RADIUS)

    def _paint_header(self, painter: QPainter) -> None:
        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(self._header_path())

        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont(theme.UI_FONT_FAMILY, 9, QFont.Weight.DemiBold))
        text_rect = QRectF(_LABEL_MARGIN, 0.0, NODE_WIDTH - _LABEL_MARGIN * 2, _HEADER_HEIGHT)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self.node.block.display_name)

    def _paint_port_labels(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor(theme.TEXT_MUTED)))
        painter.setFont(QFont(theme.UI_FONT_FAMILY, 8))

        for port_item in self.input_ports:
            y = port_item.pos().y()
            rect = QRectF(_LABEL_MARGIN, y - _ROW_HEIGHT / 2, NODE_WIDTH, _ROW_HEIGHT)
            painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, port_item.port_name)

        for port_item in self.output_ports:
            y = port_item.pos().y()
            rect = QRectF(0.0, y - _ROW_HEIGHT / 2, NODE_WIDTH - _LABEL_MARGIN, _ROW_HEIGHT)
            painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, port_item.port_name)

    def _paint_selection(self, painter: QPainter) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(theme.ACCENT), 1.5))
        body_rect = QRectF(0.0, 0.0, NODE_WIDTH, self._height)
        painter.drawRoundedRect(body_rect, _CORNER_RADIUS, _CORNER_RADIUS)

    def _header_path(self) -> QPainterPath:
        """A rounded-top, flat-bottom rectangle for the coloured title strip."""
        radius = _CORNER_RADIUS
        path = QPainterPath()
        path.moveTo(0.0, _HEADER_HEIGHT)
        path.lineTo(0.0, radius)
        path.quadTo(0.0, 0.0, radius, 0.0)
        path.lineTo(NODE_WIDTH - radius, 0.0)
        path.quadTo(NODE_WIDTH, 0.0, NODE_WIDTH, radius)
        path.lineTo(NODE_WIDTH, _HEADER_HEIGHT)
        path.closeSubpath()
        return path

    # --- port lookup --------------------------------------------------------

    def find_output_port(self, name: str) -> PortItem | None:
        """Return the output socket named `name`, if any."""
        for port_item in self.output_ports:
            if port_item.port_name == name:
                return port_item
        return None

    def find_input_port(self, name: str) -> PortItem | None:
        """Return the input socket named `name`, if any."""
        for port_item in self.input_ports:
            if port_item.port_name == name:
                return port_item
        return None

    # --- state sync ---------------------------------------------------------

    def _sync_position(self) -> None:
        self.node.position = (self.pos().x(), self.pos().y())

    def _redraw_connections(self) -> None:
        for port_item in self.input_ports + self.output_ports:
            for connection in port_item.connections:
                connection.update_path()
