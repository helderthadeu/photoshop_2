"""Use case: run the current workspace and return its results."""
from src.graph.executor import ExecutionResult, execute_workspace
from src.graph.workspace import Workspace


def run_workspace(workspace: Workspace) -> ExecutionResult:
    """Execute the workspace DAG and return per-node results.

    Thin wrapper kept so the GUI depends on the application layer rather than
    reaching directly into the executor.
    """
    return execute_workspace(workspace)
