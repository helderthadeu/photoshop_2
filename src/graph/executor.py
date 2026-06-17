"""Executes a workspace by running its nodes in topological order."""
from typing import Any

from src.graph.errors import CycleError, MissingInputError
from src.graph.node import Node
from src.graph.workspace import Workspace


class ExecutionResult:
    """Holds every node's output mapping plus the inputs each node received.

    Sink blocks (e.g. Save PGM) produce no outputs, so `inputs_of` exposes what
    reached a node — the live preview uses it to show a node's incoming image.
    """

    def __init__(self) -> None:
        self.outputs: dict[str, dict[str, Any]] = {}
        self.inputs: dict[str, dict[str, Any]] = {}

    def outputs_of(self, node_id: str) -> dict[str, Any]:
        return self.outputs.get(node_id, {})

    def inputs_of(self, node_id: str) -> dict[str, Any]:
        return self.inputs.get(node_id, {})


def execute_workspace(workspace: Workspace) -> ExecutionResult:
    """Run every node once, in dependency order, and collect results.

    Args:
        workspace: The DAG to evaluate.

    Returns:
        ExecutionResult with the outputs and gathered inputs of each node.

    Raises:
        CycleError: If the graph cannot be topologically ordered.
    """
    order = _topological_order(workspace)
    result = ExecutionResult()

    for node_id in order:
        node = workspace.nodes[node_id]
        gathered_inputs = _gather_inputs(node_id, workspace, result)
        _require_connected_inputs(node_id, node, gathered_inputs)
        result.inputs[node_id] = gathered_inputs
        result.outputs[node_id] = node.block.process(gathered_inputs, node.parameters)

    return result


def _require_connected_inputs(node_id: str, node: Node, gathered_inputs: dict[str, Any]) -> None:
    """Raise MissingInputError if any declared input port has no upstream value."""
    for port in node.block.input_ports():
        if gathered_inputs.get(port.name) is None:
            raise MissingInputError(
                f"Node '{node_id}' is missing a connection on input '{port.name}'."
            )


def _gather_inputs(
    node_id: str,
    workspace: Workspace,
    result: ExecutionResult,
) -> dict[str, Any]:
    """Collect upstream output values feeding each input port of node_id."""
    inputs: dict[str, Any] = {}
    for connection in workspace.connections:
        if connection.target_node == node_id:
            upstream = result.outputs_of(connection.source_node)
            inputs[connection.target_port] = upstream.get(connection.source_port)
    return inputs


def _topological_order(workspace: Workspace) -> list[str]:
    """Return node ids in execution order via Kahn's algorithm."""
    in_degree: dict[str, int] = {}
    for node_id in workspace.nodes:
        in_degree[node_id] = 0

    for connection in workspace.connections:
        in_degree[connection.target_node] += 1

    ready = []
    for node_id, degree in in_degree.items():
        if degree == 0:
            ready.append(node_id)

    order = []
    while ready:
        current = ready.pop()
        order.append(current)
        for connection in workspace.connections:
            if connection.source_node == current:
                target = connection.target_node
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    ready.append(target)

    if len(order) != len(workspace.nodes):
        raise CycleError("Workspace contains a cycle; cannot determine execution order.")

    return order
