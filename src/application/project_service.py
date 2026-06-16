"""Use case: serialise and reload a workspace as a JSON project file."""
import json
from pathlib import Path

from src.blocks.base import BLOCK_REGISTRY
from src.graph.connection import Connection
from src.graph.errors import GraphError
from src.graph.node import Node
from src.graph.workspace import Workspace


def save_project(workspace: Workspace, file_path: str | Path) -> None:
    """Write the workspace (nodes + connections) to a JSON file.

    Args:
        workspace: The DAG to persist.
        file_path: Destination .json path.
    """
    nodes_payload = []
    for node in workspace.nodes.values():
        nodes_payload.append(
            {
                "node_id": node.node_id,
                "block_type": type(node.block).__name__,
                "parameters": node.parameters,
                "position": list(node.position),
            }
        )

    connections_payload = []
    for connection in workspace.connections:
        connections_payload.append(
            {
                "source_node": connection.source_node,
                "source_port": connection.source_port,
                "target_node": connection.target_node,
                "target_port": connection.target_port,
            }
        )

    document = {"nodes": nodes_payload, "connections": connections_payload}
    Path(file_path).write_text(json.dumps(document, indent=2))


def load_project(file_path: str | Path) -> Workspace:
    """Reconstruct a workspace from a JSON project file.

    Args:
        file_path: Source .json path produced by save_project.

    Returns:
        A populated Workspace.

    Raises:
        GraphError: If a node references an unregistered block type.
    """
    document = json.loads(Path(file_path).read_text())
    workspace = Workspace()

    for node_payload in document["nodes"]:
        workspace.add_node(_build_node(node_payload))

    for connection_payload in document["connections"]:
        workspace.connect(
            Connection(
                source_node=connection_payload["source_node"],
                source_port=connection_payload["source_port"],
                target_node=connection_payload["target_node"],
                target_port=connection_payload["target_port"],
            )
        )

    return workspace


def _build_node(node_payload: dict) -> Node:
    block_type = node_payload["block_type"]
    block_class = BLOCK_REGISTRY.get(block_type)

    if block_class is None:
        raise GraphError(f"Unknown block type '{block_type}'.")

    return Node(
        node_id=node_payload["node_id"],
        block=block_class(),
        parameters=dict(node_payload["parameters"]),
        position=tuple(node_payload["position"]),
    )
