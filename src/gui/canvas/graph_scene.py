"""The interactive scene that mirrors a `Workspace` as movable node graphics.

`GraphScene` is the bridge between the visual canvas and the headless graph
model: dropping a block creates a `Node` in the workspace and a `NodeItem` on the
scene; dragging from an output socket to an input socket adds a validated
`Connection`. Validation (port direction, single-input, acyclicity) is delegated
to the workspace, and failures are surfaced through `connection_failed` so the
console can report them.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtWidgets import QGraphicsScene

from src.graph.connection import Connection
from src.graph.errors import ConnectionError, CycleError
from src.graph.node import Node
from src.graph.workspace import Workspace
from src.gui.canvas.connection_item import ConnectionItem
from src.gui.canvas.node_item import NodeItem
from src.gui.canvas.port_item import PortItem

_SCENE_SIZE = 6000.0


class GraphScene(QGraphicsScene):
    """A QGraphicsScene backed by a workspace DAG."""

    node_selected = Signal(object)
    node_activated = Signal(object)
    connection_failed = Signal(str)
    graph_changed = Signal()
    node_added = Signal(object)

    def __init__(self, workspace: Workspace) -> None:
        super().__init__()
        self.workspace = workspace
        self.setSceneRect(-_SCENE_SIZE / 2, -_SCENE_SIZE / 2, _SCENE_SIZE, _SCENE_SIZE)
        self._node_items: dict[str, NodeItem] = {}
        self._id_counters: dict[str, int] = {}
        self._pending: ConnectionItem | None = None
        self.selectionChanged.connect(self._emit_selection)

    # --- public graph editing ----------------------------------------------

    def add_block_node(
        self,
        block_class: type,
        scene_pos: QPointF,
        parameters: dict | None = None,
    ) -> NodeItem:
        """Place a new node for `block_class`, optionally seeding its parameters."""
        node_id = self._next_node_id(block_class.__name__)
        node = Node(
            node_id,
            block_class(),
            parameters=dict(parameters or {}),
            position=(scene_pos.x(), scene_pos.y()),
        )
        self.workspace.add_node(node)

        item = NodeItem(node)
        self.addItem(item)
        self._node_items[node_id] = item
        # A freshly placed node is not yet wired into any flow, so it cannot
        # change an existing preview: announce the addition without forcing the
        # heavy full re-execution that `graph_changed` triggers.
        self.node_added.emit(node)
        return item

    def load_workspace(self, workspace: Workspace) -> None:
        """Replace the current graph with the nodes/connections of `workspace`."""
        self.clear()
        self._node_items.clear()
        self._id_counters.clear()
        self._pending = None
        self.workspace = workspace

        for node in workspace.nodes.values():
            item = NodeItem(node)
            self.addItem(item)
            self._node_items[node.node_id] = item
            self._bump_counter(node.node_id)

        for connection in workspace.connections:
            self._restore_connection(connection)
        self.graph_changed.emit()

    def remove_selected(self) -> None:
        """Delete the selected items: standalone connections and whole nodes.

        Connections are removed first so a link that is selected on its own is
        dropped, while a selected node still takes its remaining links with it.
        """
        connections = []
        nodes = []
        for item in self.selectedItems():
            if isinstance(item, ConnectionItem):
                connections.append(item)
            elif isinstance(item, NodeItem):
                nodes.append(item)

        for connection_item in connections:
            self._remove_connection(connection_item)
        for node_item in nodes:
            self._remove_node(node_item)

        if connections or nodes:
            self.graph_changed.emit()

    # --- drag-to-connect (framework event overrides) -----------------------

    def mousePressEvent(self, event) -> None:  # standards: allow-framework-override
        port = self._port_at(event.scenePos())
        if port is not None and not port.is_input() and event.button() == Qt.MouseButton.LeftButton:
            self._begin_connection(port)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # standards: allow-framework-override
        node_item = self._node_item_at(event.scenePos())
        if node_item is not None:
            self.node_activated.emit(node_item.node)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event) -> None:  # standards: allow-framework-override
        if self._pending is not None:
            self._pending.set_free_end(event.scenePos())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # standards: allow-framework-override
        if self._pending is not None:
            self._finish_connection(event.scenePos())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # --- connection lifecycle ----------------------------------------------

    def _begin_connection(self, source_port: PortItem) -> None:
        self._pending = ConnectionItem(source_port)
        self.addItem(self._pending)

    def _finish_connection(self, scene_pos: QPointF) -> None:
        pending = self._pending
        self._pending = None
        target = self._port_at(scene_pos)

        if not self._is_valid_target(pending.source_port, target):
            self.removeItem(pending)
            return

        self._replace_existing_input(target)
        if self._register_connection(pending, target):
            self.graph_changed.emit()
        else:
            self.removeItem(pending)

    def _register_connection(self, pending: ConnectionItem, target: PortItem) -> bool:
        connection = Connection(
            pending.source_port.node_id,
            pending.source_port.port_name,
            target.node_id,
            target.port_name,
        )
        try:
            self.workspace.connect(connection)
        except (ConnectionError, CycleError) as error:
            self.connection_failed.emit(str(error))
            return False

        pending.attach_target(target)
        pending.source_port.connections.append(pending)
        target.connections.append(pending)
        return True

    def _replace_existing_input(self, target: PortItem) -> None:
        """Enforce one source per input by dropping any prior link."""
        for connection_item in list(target.connections):
            self._remove_connection(connection_item)

    # --- removal helpers ----------------------------------------------------

    def _remove_node(self, node_item: NodeItem) -> None:
        for port in node_item.input_ports + node_item.output_ports:
            for connection_item in list(port.connections):
                self._remove_connection(connection_item)

        self.workspace.remove_node(node_item.node.node_id)
        self._node_items.pop(node_item.node.node_id, None)
        self.removeItem(node_item)

    def _remove_connection(self, connection_item: ConnectionItem) -> None:
        source = connection_item.source_port
        target = connection_item.target_port

        if connection_item in source.connections:
            source.connections.remove(connection_item)
        if target is not None:
            if connection_item in target.connections:
                target.connections.remove(connection_item)
            self.workspace.disconnect(
                Connection(source.node_id, source.port_name, target.node_id, target.port_name)
            )
        self.removeItem(connection_item)

    # --- queries ------------------------------------------------------------

    def _is_valid_target(self, source: PortItem, target: PortItem | None) -> bool:
        if target is None or not target.is_input():
            return False
        return target.node_id != source.node_id

    def _port_at(self, scene_pos: QPointF) -> PortItem | None:
        for item in self.items(scene_pos):
            if isinstance(item, PortItem):
                return item
        return None

    def _node_item_at(self, scene_pos: QPointF) -> NodeItem | None:
        for item in self.items(scene_pos):
            node_item = item if isinstance(item, NodeItem) else item.parentItem()
            if isinstance(node_item, NodeItem):
                return node_item
        return None

    def _emit_selection(self) -> None:
        chosen: Node | None = None
        for item in self.selectedItems():
            if isinstance(item, NodeItem):
                chosen = item.node
                break
        self.node_selected.emit(chosen)

    def _next_node_id(self, class_name: str) -> str:
        count = self._id_counters.get(class_name, 0) + 1
        self._id_counters[class_name] = count
        return f"{class_name}_{count}"

    def _restore_connection(self, connection: Connection) -> None:
        """Rebuild a connection's graphics from a persisted edge."""
        source_node = self._node_items.get(connection.source_node)
        target_node = self._node_items.get(connection.target_node)
        if source_node is None or target_node is None:
            return

        source_port = source_node.find_output_port(connection.source_port)
        target_port = target_node.find_input_port(connection.target_port)
        if source_port is None or target_port is None:
            return

        item = ConnectionItem(source_port)
        item.attach_target(target_port)
        source_port.connections.append(item)
        target_port.connections.append(item)
        self.addItem(item)

    def _bump_counter(self, node_id: str) -> None:
        """Advance the id counter past a loaded `ClassName_N` id to avoid clashes."""
        prefix, separator, suffix = node_id.rpartition("_")
        if not separator or not suffix.isdigit():
            return
        current = self._id_counters.get(prefix, 0)
        self._id_counters[prefix] = max(current, int(suffix))
