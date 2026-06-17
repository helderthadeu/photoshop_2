"""A placed instance of a block inside the workspace."""
from dataclasses import dataclass, field
from typing import Any

from src.blocks.base import Block


@dataclass
class Node:
    """A block instance with its own id, parameter values, and canvas position.

    Parameters hold per-node values (the block itself stays stateless). Position
    is carried here so the GUI and project serialisation share one source.
    """
    node_id: str
    block: Block
    parameters: dict[str, Any] = field(default_factory=dict)
    position: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self) -> None:
        # Backfill any unset parameters with the block's declared defaults.
        defaults = self.block.default_parameters()
        for name, value in defaults.items():
            self.parameters.setdefault(name, value)
