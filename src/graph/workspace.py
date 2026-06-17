"""The workspace: the mutable DAG of nodes and connections the user builds."""
from src.graph.connection import Connection
from src.graph.errors import ConnectionError, CycleError
from src.graph.node import Node


class Workspace:
    """Holds nodes and connections and enforces DAG validity.

    A workspace may contain several disconnected sub-graphs, which is how the
    spec's "two or more images in the workspace" requirement is satisfied.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._connections: list[Connection] = []

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    @property
    def connections(self) -> list[Connection]:
        return self._connections

    def add_node(self, node: Node) -> None:
        """Register a node, keyed by its id."""
        if node.node_id in self._nodes:
            raise ConnectionError(f"Duplicate node id '{node.node_id}'.")
        self._nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and every connection touching it."""
        self._nodes.pop(node_id, None)

        remaining = []
        for connection in self._connections:
            if connection.source_node != node_id and connection.target_node != node_id:
                remaining.append(connection)
        self._connections = remaining

    def connect(self, connection: Connection) -> None:
        """Add a connection after validating ports and acyclicity."""
        self._validate_endpoints(connection)

        if self._would_create_cycle(connection):
            raise CycleError(
                f"Connecting {connection.source_node} → {connection.target_node} "
                f"would create a cycle."
            )

        self._connections.append(connection)

    def disconnect(self, connection: Connection) -> None:
        """Remove a previously added connection if present."""
        if connection in self._connections:
            self._connections.remove(connection)

    def _validate_endpoints(self, connection: Connection) -> None:
        source = self._nodes.get(connection.source_node)
        target = self._nodes.get(connection.target_node)

        if source is None or target is None:
            raise ConnectionError("Connection references an unknown node.")

        output_names = []
        for port in source.block.output_ports():
            output_names.append(port.name)
        if connection.source_port not in output_names:
            raise ConnectionError(
                f"'{connection.source_port}' is not an output of {connection.source_node}."
            )

        input_names = []
        for port in target.block.input_ports():
            input_names.append(port.name)
        if connection.target_port not in input_names:
            raise ConnectionError(
                f"'{connection.target_port}' is not an input of {connection.target_node}."
            )

    def _would_create_cycle(self, candidate: Connection) -> bool:
        """Return True if adding candidate makes target reach back to source."""
        adjacency = self._build_adjacency()
        adjacency.setdefault(candidate.source_node, []).append(candidate.target_node)

        visited: set[str] = set()
        return self._reaches(candidate.target_node, candidate.source_node, adjacency, visited)

    def _build_adjacency(self) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {}
        for connection in self._connections:
            adjacency.setdefault(connection.source_node, []).append(connection.target_node)
        return adjacency

    def _reaches(
        self,
        start: str,
        goal: str,
        adjacency: dict[str, list[str]],
        visited: set[str],
    ) -> bool:
        if start == goal:
            return True

        visited.add(start)
        for neighbour in adjacency.get(start, []):
            if neighbour not in visited:
                if self._reaches(neighbour, goal, adjacency, visited):
                    return True
        return False
