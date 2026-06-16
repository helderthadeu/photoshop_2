"""Domain-specific exceptions raised by the graph engine."""


class GraphError(Exception):
    """Base class for all workspace/graph errors."""


class CycleError(GraphError):
    """Raised when a connection would introduce a cycle in the DAG."""


class ConnectionError(GraphError):
    """Raised when a connection references unknown nodes or ports."""


class MissingInputError(GraphError):
    """Raised when a node is executed without a required input being connected."""
