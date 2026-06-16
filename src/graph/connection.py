"""A directed edge linking one block's output port to another's input port."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Connection:
    """Links source_node.source_port → target_node.target_port."""
    source_node: str
    source_port: str
    target_node: str
    target_port: str
