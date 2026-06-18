"""Use case: run the current workspace and return its results."""
from src.graph.executor import (
    ExecutionResult,
    NodeCache,
    ProgressCallback,
    execute_workspace,
)
from src.graph.workspace import Workspace


def run_workspace(
    workspace: Workspace,
    cache: NodeCache | None = None,
    skip_incomplete: bool = False,
    progress: ProgressCallback | None = None,
) -> ExecutionResult:
    """Execute the workspace DAG and return per-node results.

    Thin wrapper kept so the GUI depends on the application layer rather than
    reaching directly into the executor. `cache` memoises unchanged nodes,
    `skip_incomplete` tolerates unwired nodes, and `progress` traces computed
    nodes — see `execute_workspace`.
    """
    return execute_workspace(
        workspace,
        cache=cache,
        skip_incomplete=skip_incomplete,
        progress=progress,
    )
