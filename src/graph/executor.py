"""Executes a workspace by running its nodes in topological order."""
import time
from dataclasses import dataclass
from typing import Any, Callable

from src.graph.errors import CycleError, MissingInputError
from src.graph.node import Node
from src.graph.workspace import Workspace

# A node's cache entry: the signature it was computed for and the outputs it
# produced. The signature folds in the block type, its parameters, and every
# upstream node's signature, so an entry is reused only when nothing that feeds
# the node has changed.
NodeCache = dict[str, tuple[tuple, dict[str, Any]]]


@dataclass(frozen=True)
class NodeProgress:
    """A progress event emitted while a node is actually computed.

    Cache hits are silent — only real work is reported, so the event stream is a
    faithful trace of where execution time is spent. `phase` is "start" (emitted
    just before processing) or "done" (after, carrying the measured `elapsed`).
    """
    node_id: str
    display_name: str
    phase: str
    elapsed: float = 0.0


# Called synchronously as nodes run; the caller decides how to surface progress.
ProgressCallback = Callable[[NodeProgress], None]


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


def execute_workspace(
    workspace: Workspace,
    cache: NodeCache | None = None,
    skip_incomplete: bool = False,
    progress: ProgressCallback | None = None,
) -> ExecutionResult:
    """Run every node once, in dependency order, and collect results.

    Args:
        workspace: The DAG to evaluate.
        cache: Optional per-node memo. When supplied, a node whose signature is
            unchanged reuses its previous outputs instead of recomputing; stale
            entries for removed nodes are pruned. Pass ``None`` for a clean run.
        skip_incomplete: When True, a node with an unconnected required input is
            skipped (it and its dependents simply produce nothing) instead of
            raising. The live preview uses this so a freshly dropped, unwired
            node never aborts the run; batch/strict runs leave it False.
        progress: Optional callback notified as each computed node starts and
            finishes (cache hits are not reported). Lets the GUI trace progress.

    Returns:
        ExecutionResult with the outputs and gathered inputs of each node.

    Raises:
        CycleError: If the graph cannot be topologically ordered.
        MissingInputError: If a required input is unconnected and
            ``skip_incomplete`` is False.
    """
    order = _topological_order(workspace)
    result = ExecutionResult()
    signatures: dict[str, tuple] = {}

    for node_id in order:
        node = workspace.nodes[node_id]
        gathered_inputs = _gather_inputs(node_id, workspace, result)

        if _has_missing_inputs(node, gathered_inputs):
            if skip_incomplete:
                continue
            _raise_missing_input(node_id, node, gathered_inputs)

        result.inputs[node_id] = gathered_inputs
        signature = _signature_of(node, node_id, workspace, signatures)
        signatures[node_id] = signature
        result.outputs[node_id] = _run_node(node, gathered_inputs, signature, cache, progress)

    if cache is not None:
        _prune_cache(cache, workspace)
    return result


def _run_node(
    node: Node,
    gathered_inputs: dict[str, Any],
    signature: tuple,
    cache: NodeCache | None,
    progress: ProgressCallback | None,
) -> dict[str, Any]:
    """Return the node's outputs, reusing the cache and reporting real work.

    A cache hit returns instantly and silently; a miss is timed and bracketed by
    "start"/"done" progress events so the cost of each computed node is visible.
    """
    if _is_cache_hit(node.node_id, signature, cache):
        return cache[node.node_id][1]

    _report(progress, node, "start", 0.0)
    started = time.perf_counter()
    outputs = node.block.process(gathered_inputs, node.parameters)
    elapsed = time.perf_counter() - started

    if cache is not None:
        cache[node.node_id] = (signature, outputs)
    _report(progress, node, "done", elapsed)
    return outputs


def _is_cache_hit(node_id: str, signature: tuple, cache: NodeCache | None) -> bool:
    """True when the cache holds an entry computed for this exact signature."""
    if cache is None:
        return False
    entry = cache.get(node_id)
    return entry is not None and entry[0] == signature


def _report(progress: ProgressCallback | None, node: Node, phase: str, elapsed: float) -> None:
    """Forward a progress event to the callback when one is registered."""
    if progress is not None:
        progress(NodeProgress(node.node_id, node.block.display_name, phase, elapsed))


def _signature_of(
    node: Node,
    node_id: str,
    workspace: Workspace,
    signatures: dict[str, tuple],
) -> tuple:
    """Build a content signature folding in block type, params, and upstream sigs."""
    upstream = []
    for connection in workspace.connections:
        if connection.target_node == node_id:
            source_signature = signatures.get(connection.source_node, ())
            upstream.append(
                (connection.target_port, connection.source_port, source_signature)
            )
    upstream.sort()

    return (node.block.__class__.__name__, _parameters_signature(node.parameters), tuple(upstream))


def _parameters_signature(parameters: dict[str, Any]) -> tuple:
    """Render parameter values into a stable, hashable, comparable form."""
    items = []
    for key in sorted(parameters):
        items.append((key, repr(parameters[key])))
    return tuple(items)


def _prune_cache(cache: NodeCache, workspace: Workspace) -> None:
    """Drop cache entries for nodes no longer in the workspace."""
    stale = set(cache) - set(workspace.nodes)
    for node_id in stale:
        del cache[node_id]


def _has_missing_inputs(node: Node, gathered_inputs: dict[str, Any]) -> bool:
    """True when any declared input port has no upstream value."""
    for port in node.block.input_ports():
        if gathered_inputs.get(port.name) is None:
            return True
    return False


def _raise_missing_input(node_id: str, node: Node, gathered_inputs: dict[str, Any]) -> None:
    """Raise MissingInputError for the first input port without an upstream value."""
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
