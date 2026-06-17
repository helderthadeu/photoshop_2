"""Left-side palette listing every registered block, grouped by category.

Blocks are read from `BLOCK_REGISTRY` and shown in a tree under coloured
category headers. Each leaf is draggable: dropping it on the canvas spawns a node
(see `GraphView`). The drag payload is the block's class name, carried in the
`BLOCK_MIME_TYPE` mime format.
"""
from __future__ import annotations

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QColor, QDrag, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.blocks.base import BLOCK_REGISTRY
from src.gui import theme
from src.gui.drag_mime import BLOCK_MIME_TYPE

_CLASS_NAME_ROLE = Qt.ItemDataRole.UserRole
_CATEGORY_ORDER = ["Interface", "Point", "Local", "Analysis"]
_SWATCH_SIZE = 12


class BlockLibrary(QWidget):
    """A dockable panel of draggable processing blocks."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(_panel_title("BLOCK LIBRARY"))
        self._tree = _BlockTree()
        layout.addWidget(self._tree)
        self._populate()

    def _populate(self) -> None:
        """Group registered blocks under their category headers."""
        grouped = _blocks_by_category()
        for category in _ordered_categories(grouped):
            header = self._add_category_header(category)
            for class_name, display_name in grouped[category]:
                self._add_block_leaf(header, class_name, display_name)
        self._tree.expandAll()

    def _add_category_header(self, category: str) -> QTreeWidgetItem:
        header = QTreeWidgetItem(self._tree, [category.upper()])
        header.setFlags(Qt.ItemFlag.ItemIsEnabled)
        header.setForeground(0, QColor(theme.TEXT_MUTED))
        return header

    def _add_block_leaf(self, header: QTreeWidgetItem, class_name: str, display_name: str) -> None:
        leaf = QTreeWidgetItem(header, [display_name])
        leaf.setData(0, _CLASS_NAME_ROLE, class_name)
        leaf.setIcon(0, _category_swatch(self._category_of(class_name)))

    def _category_of(self, class_name: str) -> str:
        return BLOCK_REGISTRY[class_name]().category


class _BlockTree(QTreeWidget):
    """A tree whose leaves start a drag carrying the block class name."""

    def __init__(self) -> None:
        super().__init__()
        self.setHeaderHidden(True)
        self.setIndentation(12)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def startDrag(self, supported_actions) -> None:  # standards: allow-framework-override
        item = self.currentItem()
        class_name = item.data(0, _CLASS_NAME_ROLE) if item else None
        if not class_name:
            return

        mime = QMimeData()
        mime.setData(BLOCK_MIME_TYPE, class_name.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


def _blocks_by_category() -> dict[str, list[tuple[str, str]]]:
    """Map each category to its (class_name, display_name) pairs."""
    grouped: dict[str, list[tuple[str, str]]] = {}
    for class_name, block_class in BLOCK_REGISTRY.items():
        instance = block_class()
        grouped.setdefault(instance.category, []).append((class_name, instance.display_name))
    return grouped


def _ordered_categories(grouped: dict[str, list[tuple[str, str]]]) -> list[str]:
    """List known categories first in a fixed order, then any extras."""
    ordered = []
    for category in _CATEGORY_ORDER:
        if category in grouped:
            ordered.append(category)
    for category in grouped:
        if category not in ordered:
            ordered.append(category)
    return ordered


def _category_swatch(category: str) -> QPixmap:
    """A small filled square in the category colour, used as a leaf icon."""
    pixmap = QPixmap(_SWATCH_SIZE, _SWATCH_SIZE)
    pixmap.fill(theme.category_color(category))
    return pixmap


def _panel_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
    return label
